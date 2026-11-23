import sys
import types

import torch
import transformers
import transformers.pytorch_utils


# =======================================================================
# LXT DEPENDENCY SHIM: Inject missing HF functions (v4.57+ compatibility)
# =======================================================================
def find_pruneable_heads_and_indices(heads, n_heads, head_size, already_pruned_heads):
    mask = torch.ones(n_heads, head_size)
    heads = set(heads) - already_pruned_heads
    for head in heads:
        mask[head] = 0
    mask = mask.view(-1).contiguous().eq(1)
    index = torch.arange(len(mask))[mask].long()
    return heads, index

def prune_linear_layer(layer, index, dim=0):
    index = index.to(layer.weight.device)
    W = layer.weight.index_select(dim, index).clone().detach()
    if layer.bias is not None:
        b = layer.bias.clone().detach() if dim == 1 else layer.bias[index].clone().detach()
    new_size = list(layer.weight.size())
    new_size[dim] = len(index)
    new_layer = torch.nn.Linear(new_size[1], new_size[0], bias=layer.bias is not None).to(layer.weight.device)
    new_layer.weight.requires_grad = False
    new_layer.weight.copy_(W.contiguous())
    new_layer.weight.requires_grad = True
    if layer.bias is not None:
        new_layer.bias.requires_grad = False
        new_layer.bias.copy_(b.contiguous())
        new_layer.bias.requires_grad = True
    return new_layer

def apply_chunking_to_forward(forward_fn, chunk_size, chunk_dim, *input_tensors):
    return forward_fn(*input_tensors)

transformers.pytorch_utils.find_pruneable_heads_and_indices = find_pruneable_heads_and_indices
transformers.pytorch_utils.prune_linear_layer = prune_linear_layer
transformers.pytorch_utils.apply_chunking_to_forward = apply_chunking_to_forward

# Shim removed transformers.modeling_attn_mask_utils (needed by lxt.efficient.models.bert)
try:
    import transformers.modeling_attn_mask_utils  # noqa: F401
except ModuleNotFoundError:
    _attn_mask_mod = types.ModuleType("transformers.modeling_attn_mask_utils")

    def _prepare_4d_attention_mask_for_sdpa(mask, dtype, tgt_len=None):
        bsz, src_len = mask.shape
        tgt_len = tgt_len if tgt_len is not None else src_len
        expanded = mask[:, None, None, :].expand(bsz, 1, tgt_len, src_len).to(dtype)
        inverted = 1.0 - expanded
        return inverted.masked_fill(inverted.to(torch.bool), torch.finfo(dtype).min)

    def _prepare_4d_causal_attention_mask_for_sdpa(
        attention_mask, input_shape, inputs_embeds, past_key_values_length, sliding_window=None
    ):
        bsz, tgt_len = input_shape
        src_len = tgt_len + past_key_values_length
        dtype = inputs_embeds.dtype
        device = inputs_embeds.device
        causal_mask = torch.full((tgt_len, src_len), torch.finfo(dtype).min, device=device, dtype=dtype)
        mask_cond = torch.arange(src_len, device=device)
        causal_mask.masked_fill_(mask_cond < (mask_cond + 1).view(src_len, 1)[-tgt_len:], 0)
        causal_mask = causal_mask[None, None, :, :].expand(bsz, 1, tgt_len, src_len)
        if attention_mask is not None:
            pad_mask = _prepare_4d_attention_mask_for_sdpa(attention_mask, dtype, tgt_len=tgt_len)
            causal_mask = causal_mask + pad_mask
        return causal_mask

    _attn_mask_mod._prepare_4d_attention_mask_for_sdpa = _prepare_4d_attention_mask_for_sdpa
    _attn_mask_mod._prepare_4d_causal_attention_mask_for_sdpa = _prepare_4d_causal_attention_mask_for_sdpa
    sys.modules["transformers.modeling_attn_mask_utils"] = _attn_mask_mod
    transformers.modeling_attn_mask_utils = _attn_mask_mod

import lxt.efficient  # Import LXT to intercept its patcher

# =======================================================================
# LXT DICTIONARY SHIM: Intercept and repair ALL_ATTENTION_FUNCTIONS
# =======================================================================
original_monkey_patch = lxt.efficient.monkey_patch

def safe_monkey_patch(module, patch_map=None, verbose=False):
    # 1. Run the original LXT patcher (which breaks the attention registry)
    original_monkey_patch(module=module, patch_map=patch_map, verbose=verbose)
    
    # 2. Immediately repair the damage across all loaded transformers models
    for mod_name, mod in list(sys.modules.items()):
        if (mod_name.startswith("transformers.models.") \
            or mod_name.startswith("transformers.modeling_")) \
                and hasattr(mod, "ALL_ATTENTION_FUNCTIONS"):
            registry = mod.ALL_ATTENTION_FUNCTIONS
            
            # If LXT replaced it with a raw dict, upgrade it to support .get_interface()
            if type(registry) is dict:  
                class LXTCompatRegistry(dict):
                    def get_interface(self, attn_implementation, eager_attention_forward):
                        return self.get(attn_implementation, eager_attention_forward)
                
                mod.ALL_ATTENTION_FUNCTIONS = LXTCompatRegistry(registry)

# Overwrite LXT's function with our safe wrapper
lxt.efficient.monkey_patch = safe_monkey_patch