import torch
from torch import Tensor


def filter_top_result(result: dict[str, Tensor], device: torch.device):
    
    filtered_result = {
        'scores': torch.tensor([], device=device),
        'labels': torch.tensor([], device=device),
        'boxes': torch.tensor([], device=device)
    }
    
    unique_labels = torch.unique(result['labels'])

    for unique_label in unique_labels:
        mask = (result['labels'] == unique_label)
        label_scores: Tensor = result['scores'][mask]
        label_boxes = result['boxes'][mask]

        current_label_scores = label_scores[:, unique_label]
        highest_score_idx = torch.argmax(current_label_scores)
        
        ## List of 1d tensors
        filtered_result['labels'] = torch.cat((filtered_result['labels'], unique_label.view(1).to(device)))

        ## List of 1d tensors
        filtered_result['scores'] = torch.cat((filtered_result['scores'], current_label_scores[highest_score_idx].view(1).to(device)))

        ## List of (1, 4) tensors (boxes)
        filtered_result['boxes'] = torch.cat((filtered_result['boxes'], label_boxes[highest_score_idx].view(1, 4).to(device)))

    return filtered_result