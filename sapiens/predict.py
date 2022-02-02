import os
import numpy as np
from sapiens.roberta import RoBERTaSeq2Seq
# register loss function
# noinspection PyUnresolvedReferences
from sapiens.smooth_masked_lm import SmoothMaskedLmLoss
import torch

MODEL_VERSIONS = ['v1']

CACHED_MODELS = {}


def load_cached_model(model_dir, checkpoint_name, cache=True):
    model_key = (model_dir, checkpoint_name)
    if not cache or model_key not in CACHED_MODELS:
        CACHED_MODELS[model_key] = RoBERTaSeq2Seq.load(model_dir, checkpoint_name)
    return CACHED_MODELS[model_key]


def get_model_path(model_version):
    src_root = os.path.dirname(__file__)
    return os.path.join(src_root, 'models', model_version)


def predict_scores(seq, chain_type, model_version='latest', return_all_hiddens=False):
    """Predict Sapiens residue scores for each position in a given sequence

    @param seq: Antibody variable region sequence
    @param chain_type: Chain type (H = heavy, L = light). Same model is used for kappa and lambda.
    @param model_version: Model instance or version of the model: latest, v1, etc
    @param return_all_hiddens: Return a tuple with (probs, weights_dict)
    @return: Pandas DataFrame with one row for each position and one column for each residue type
    """
    assert '/' not in model_version
    if model_version == 'latest':
        model_version = MODEL_VERSIONS[-1]
    model_dir = get_model_path(model_version)
    if chain_type == 'H':
        checkpoint_name = 'checkpoint_vh.pt'
    elif chain_type in ['K', 'L']:
        checkpoint_name = 'checkpoint_vl.pt'
    else:
        raise ValueError(f'Unknown chain type {chain_type}')
    model = load_cached_model(model_dir, checkpoint_name)
    return model.predict_scores(seq, return_all_hiddens=return_all_hiddens)


def predict_best_score(seq, chain_type, model_version='latest'):
    scores = predict_scores(seq, chain_type, model_version=model_version)
    return ''.join(scores.idxmax(axis=1).values)


def predict_masked(seq, chain_type, model_version='latest'):
    best_score_seq = predict_best_score(seq, chain_type, model_version=model_version)
    return ''.join([b if a in '*X' else a for a, b in zip(seq, best_score_seq)])


def predict_residue_embedding(seq, chain_type, layer=None):
    pred, extra = predict_scores(seq, chain_type=chain_type, model_version='latest', return_all_hiddens=True)
    embed = extra['inner_states']
    if layer is not None:
        return embed[layer][1:-1,0,:].cpu().numpy()
    return np.array([e[1:-1,0,:].cpu().numpy() for e in embed])


def predict_sequence_embedding(seq, chain_type, layer=None):
    return predict_residue_embedding(seq, chain_type, layer=layer).mean(axis=-2)
