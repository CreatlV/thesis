from typing import Optional, cast
import torch
from transformers import (
    Trainer,
    ConditionalDetrForObjectDetection,
    ConditionalDetrImageProcessor,
)
from torch.utils.data import DataLoader
import evaluation

def get_collate_fn(feature_extractor: ConditionalDetrImageProcessor):
    def collate_fn(batch):
        pixel_values = [item["pixel_values"] for item in batch]
        encoding = feature_extractor.pad(pixel_values, return_tensors="pt")
        labels = [item["labels"].__dict__["data"] for item in batch]
        batch = {}  # collated batch
        batch["pixel_values"] = encoding["pixel_values"]
        batch["pixel_mask"] = encoding["pixel_mask"]
        batch["labels"] = labels
        return batch

    return collate_fn


class CustomCDetrTrainer(Trainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if isinstance(self.model, ConditionalDetrForObjectDetection):
            self.model = cast(ConditionalDetrForObjectDetection, self.model)
        else:
            raise ValueError(
                "CustomCDetrTrainer only works with ConditionalDetrForObjectDetection"
            )

        if not isinstance(self.tokenizer, ConditionalDetrImageProcessor):
            self.tokenizer = cast(ConditionalDetrImageProcessor, self.tokenizer)
        
        self.data_collator = get_collate_fn(self.tokenizer)

    def create_optimizer(self):
        # Separate DETR and backbone parameters
        detr_params = [p for n, p in self.model.named_parameters() if 'backbone' not in n]
        backbone_params = [p for n, p in self.model.named_parameters() if 'backbone' in n]

        # Group the parameters with their corresponding learning rates
        grouped_parameters = [
            {"params": detr_params, "lr": 1e-4},
            {"params": backbone_params, "lr": 1e-5}
        ]

        # Create the custom optimizer with grouped parameters
        optimizer = torch.optim.AdamW(grouped_parameters)
        self.optimizer = optimizer

    def evaluation_loop(
        self,
        dataloader: DataLoader,
        description: str,
        prediction_loss_only: Optional[bool] = None,
        ignore_keys: Optional[list[str]] = None,
        metric_key_prefix: str = "eval",
    ):

        map_evaluation = evaluation.run_evaluation_cond(
            self.model,
            self.tokenizer,
            dataloader,
            self.args.device,
            plot=False,
        )

        metrics = super().evaluation_loop(
            dataloader,
            description,
            prediction_loss_only,
            ignore_keys,
            metric_key_prefix,
        )

        if not metrics.metrics:
            raise ValueError("The `metrics` should have a value")

        ## Add all metrics from map_evaluation to metrics, preficed with metric_key_prefix
        for key, value in map_evaluation.items():
            if isinstance(value, torch.Tensor):
                value = value.item() if value.numel() == 1 else value.tolist()

            # If value is a scalar, round it to 4 decimal places
            if isinstance(value, (int, float)):
                value = round(value, 4)
                metrics.metrics[metric_key_prefix + "_" + key] = value

        return metrics
