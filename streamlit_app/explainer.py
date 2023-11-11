import shap


def explain(images):
    topk = 4
    batch_size = 50
    n_evals = 10000

    # define a masker that is used to mask out partitions of the input image.
    masker_blur = shap.maskers.Image("blur(128,128)", Xtr[0].shape)

    # create an explainer with model and image masker
    explainer = shap.Explainer(predict, masker_blur, output_names=["Nothing", "Highlight"])

    # feed only one image
    # here we explain two images using 100 evaluations of the underlying model to estimate the SHAP values
    shap_values = explainer(
        Xtr[1:2],
        max_evals=n_evals,
        batch_size=batch_size,
        outputs=shap.Explanation.argsort.flip[:topk],
    )