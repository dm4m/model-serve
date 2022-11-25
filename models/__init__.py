import torch
from transformers import RoFormerModel, RoFormerTokenizer

model = RoFormerModel.from_pretrained("./roformer_chinese_sim_char_ft_base")
tokenizer = RoFormerTokenizer.from_pretrained("./roformer_chinese_sim_char_ft_base")
use_gpu = True
device = torch.device("cuda" if (use_gpu and torch.cuda.is_available()) else "cpu")


def init_app(app):
    if use_gpu:
        model.to(device)
    return model, tokenizer, use_gpu, device
