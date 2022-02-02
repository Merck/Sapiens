import numpy as np
from sapiens.predict import predict_masked, predict_scores


def test_predict_scores():
    seq = 'QVQLVQSGVEVKKPGASVKVSCKASGYTFTNYYMYWVRQAPGQGLEWMGGINPSNGGTNFNEKFKNRVTLTTDSSTTTAYMELKSLQFDDTAVYYCARRDYRFDMGFDYWGQGTTVTVSS'
    pred = predict_scores(
        seq=seq,
        chain_type='H',
        model_version='latest'
    )
    assert pred.shape == (len(seq), 20), 'Expected matrix (length of sequence * 20 amino acids)'
    assert (pred.idxmax(axis=1).values == np.array(list(seq))).sum() > 100, 'Prediction should be similar to input sequence'


def test_predict_masked():
    pred = predict_masked('**QLV*SGVEVKKPGASVKVSCKASGYTFTNYYMYWVRQAPGQGLEWMGGINPSNGGTNFNEKFKNRVTLTTDSSTTTAYMELKSLQFDDTAVYYCARRDYRFDMGFDYWGQGTTVTVSS', 'H')
    assert pred.startswith('QVQLVQ')