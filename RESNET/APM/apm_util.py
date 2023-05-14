from torchvision.transforms import Resize, CenterCrop, ToPILImage
from torchvision.transforms import Normalize
from torch import topk


def inverse_transform(image):
    # inverse transform generated by request from ChatGPT by supplying the print(transform) from below
    inv_normalize = Normalize(
        mean=[-0.485 / 0.229, -0.456 / 0.224, -0.406 / 0.225],
        std=[1 / 0.229, 1 / 0.224, 1 / 0.225]
    )

    image = inv_normalize(image)
    image = ToPILImage()(image)
    image = CenterCrop(size=(235, 235))(image)
    image = Resize(size=(224, 224), interpolation=2)(image)
    return image

def print_topk(categories, probabilities, k):
    """Print top categories per image"""
    topk_prob, topk_catid = topk(probabilities, k)
    for i in range(topk_prob.size(0)):
        print(categories[topk_catid[i]], topk_prob[i].item())

def compare_probs(categories, prob_before, prob_after, verbose=False):
    """
    Print probability of the classification of original image
    before and after spoofing.
    """
    prob_before, id = topk(prob_before, 1)
    prob_before, id = prob_before[0], id[0]
    prob_after = prob_after[id].detach()

    if verbose:
        print("Original category: {}".format(categories[id]))
        print("Probability before: {}".format(prob_before))
        print("Probability after: {}".format(prob_after))
    
    return categories[id], prob_before, prob_after
