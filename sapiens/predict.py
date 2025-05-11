import numpy as np
import torch
from transformers import RobertaForMaskedLM, RobertaTokenizer
import pandas as pd

CACHED_MODELS = {}
CACHED_TOKENIZERS = {}
DEFAULT_TOKENIZER_PATH = "prihodad/biophi-sapiens1-tokenizer"


def load_cached_model(model_key, cache=True):
    if not cache or model_key not in CACHED_MODELS:
        CACHED_MODELS[model_key] = RobertaForMaskedLM.from_pretrained(model_key)
    return CACHED_MODELS[model_key]


def load_cached_tokenizer(tokenizer_key, cache=True):
    if not cache or tokenizer_key not in CACHED_TOKENIZERS:
        CACHED_TOKENIZERS[tokenizer_key] = RobertaTokenizer.from_pretrained(tokenizer_key)
    return CACHED_TOKENIZERS[tokenizer_key]


def predict_scores(seq, chain_type, checkpoint_path=None, probs=True, return_embeddings=False, layer=None, tokenizer_path=DEFAULT_TOKENIZER_PATH):
    """Predict Sapiens residue scores for each position in a given sequence

    @param seq: Antibody variable region sequence
    @param chain_type: Chain type (H = heavy, L = light). Same model is used for kappa and lambda.
    @param checkpoint_path: Huggingface hub path or local path to load the model from
    @param probs: Return probabilities (apply softmax). If False, returns logits.
    @param return_embeddings: Return a tuple with (probs, embeddings)
    @param layer: Layer of embeddings to return when return_embeddings=True. None means all layers, use -1 for last layer.
    @param tokenizer_path: Huggingface hub path or local path to load tokenizer from
    @return: Pandas DataFrame with one row for each position and one column for each residue type
    """
    if checkpoint_path is None:
        if chain_type == 'H':
            checkpoint_path = 'prihodad/biophi-sapiens1-vh'
        elif chain_type in ['K', 'L']:
            checkpoint_path = 'prihodad/biophi-sapiens1-vl'
        else:
            raise ValueError(f'Unknown chain type {chain_type}')
    model = load_cached_model(checkpoint_path)
    tokenizer = load_cached_tokenizer(tokenizer_path)
    encoded_input = tokenizer(seq, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input, output_hidden_states=return_embeddings)
        logits = output.logits[0][1:-1].cpu()
    index_to_token = {idx: token for token, idx in tokenizer.get_vocab().items()}
    probs = pd.DataFrame(
        logits.numpy() if not probs else torch.softmax(logits, dim=-1).numpy(),
        columns=[index_to_token[i] for i in range(logits.shape[1])]
    )[list('ACDEFGHIKLMNPQRSTVWY')]
    if return_embeddings:
        if layer is None:
            embeddings = np.array([states[0,1:-1,:] for states in output.hidden_states])
        else:
            embeddings = output.hidden_states[layer][0,1:-1,:].cpu().numpy()
        return probs, embeddings
    return probs


def predict_best_score(seq, chain_type, checkpoint_path=None):
    scores = predict_scores(seq, chain_type, checkpoint_path=checkpoint_path)
    return ''.join(scores.idxmax(axis=1).values)


def predict_masked(seq, chain_type, checkpoint_path=None):
    best_score_seq = predict_best_score(seq, chain_type, checkpoint_path=checkpoint_path)
    return ''.join([b if a in '*X' else a for a, b in zip(seq, best_score_seq)])


def predict_residue_embedding(seq, chain_type, layer=None, checkpoint_path=None):
    pred, embeddings = predict_scores(seq, chain_type=chain_type, checkpoint_path=checkpoint_path, return_embeddings=True, layer=layer)
    return embeddings


def predict_sequence_embedding(seq, chain_type, layer=None, checkpoint_path=None):
    return predict_residue_embedding(seq, chain_type, layer=layer, checkpoint_path=checkpoint_path).mean(axis=-2)
