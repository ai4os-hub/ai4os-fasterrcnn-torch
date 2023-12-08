import json
from webargs import fields, validate
from marshmallow import Schema, ValidationError

from fasterrcnn_pytorch_api import configs


class MyCustomFieldForJson(fields.String):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.get("metadata", {})
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return json.loads(value)
        except json.JSONDecodeError as err:
            raise ValidationError(f"Invalid JSON: `{err}`")

    def _validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError(
                "Invalid value. Expected a dictionary."
            )

        for k1, v1 in value.items():
            if not isinstance(v1, dict):
                raise ValidationError(
                    f"Invalid value for {k1}. Expected a dictionary."
                )

            for k2, v2 in v1.items():
                if k2 == "p":
                    if not isinstance(v2, float) or not (
                        0 <= v2 <= 1.0
                    ):
                        raise ValidationError(
                            f"Invalid value for 'p' in {k2}: {v2}."
                            "It must be a float between 0 and 1."
                        )
                elif k2 in [
                    "max_w_size",
                    "max_h_size",
                    "num_holes",
                    "blur_limit",
                ]:
                    if not isinstance(v2, int) or v2 < 0:
                        raise ValidationError(
                            f"Invalid value for '{k2}' in {k1}: {v2}."
                            " It must be a non-negative integer."
                        )
                elif k2 in ["scale_limit", "shift_limit"]:
                    if not isinstance(v2, float) or not isinstance(
                        v2, (float, float)
                    ):
                        raise ValidationError(
                            f"Invalid value for '{k2}': {v2}."
                            "It must be a float or (float, float)."
                        )
                elif k2 == "rotate_limit":
                    if not isinstance(v2, int) or not isinstance(
                        v2, (int, int)
                    ):
                        raise ValidationError(
                            f"Invalid value for '{k2}': {v2}."
                            "It must be an int or (int, int)."
                        )


class TrainArgsSchema(Schema):
    class Meta:
        ordered = True

    model = fields.Str(
        required=False,
        load_default='fasterrcnn_resnet50_fpn_v2',
        metadata={
            "description": "Name of the model.",
            "enum": configs.BACKBONES,
        },
    )

    data_config = fields.Str(
        required=True,
        metadata={
            "description": "Path to the data_config.yaml file. It can be an absolute path or "
            "e.g. my_dataset/data_config.yaml, if your data is in the data (configs.DATA_PATH) directory."
        },
    )

    use_train_aug = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Whether to use train augmentation, "
            "uses some advanced augmentation that may make training "
            "difficult when used with mosaic. If true, it uses "
            "the options in aug_training_option. You can change "
            "that to have custom augmentation.",
            "enum": [True, False],
        },
    )

    aug_option = MyCustomFieldForJson(
        load_default=json.dumps(configs.DATA_AUG_OPTION),
        metadata={
            "description": "Augmentation options.\n"
            "blur_limit (int) - maximum kernel size for blurring"
            "the input image.\n"
            "p (float) - probability of applying the transform.\n"
            "shift_limit ((float, float) or float) - shift factor range for"
            "both height and width.\n"
            "scale_limit ((float, float) or float) - scaling factor range.\n"
            "rotate_limit ((int, int) or int) - rotation range.\n"
            "num_holes (int) - number of regions to zero out.\n"
            "max_h_size (int) - maximum height of the hole.\n"
            "max_w_size (int) - maximum width of the hole.\n"
        },
    )

    device = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Computation/training device, default is GPU if "
            "GPU present.",
            "enum": [True, False],
        },
    )

    epochs = fields.Int(
        required=False,
        load_default=4,
        metadata={"description": "Number of epochs to train."},
    )

    workers = fields.Int(
        required=False,
        load_default=4,
        metadata={
            "description": "Number of workers for data processing/transforms"
            "/augmentations."
        },
    )

    batch = fields.Int(
        required=False,
        load_default=4,
        metadata={"description": "Batch size to load the data."},
    )

    lr = fields.Float(
        required=False,
        load_default=0.001,
        metadata={"description": "Learning rate for training."},
    )

    imgsz = fields.Int(
        required=False,
        load_default=640,
        metadata={
            "description": "Image size to feed to the network."
        },
    )

    no_mosaic = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Pass this to not use mosaic augmentation.",
            "enum": [True, False],
        },
    )

    cosine_annealing = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Use cosine annealing warm restarts.",
            "enum": [True, False],
        },
    )

    weights = fields.Str(
        required=False,
        load_default=None,
        metadata={
            "description": "path to model directory with ckpt(last_model.pth) "
            "if custom pretrain weights are used. "
            "It should be an absolute path like 'path/to/ckpt_dir' or "
            "a path from model (configs.MODEL_DIR) directory (for example: 'timestamps/weights')."
            "To see the list of available trained models, please use the metadata methods."
        },
    )

    resume_training = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "If using custom pretrained weights, resume training from "
            "the last step of the provided checkpoint. If True, the path to "
            "the weights should be specified in the argument weights.",
            "enum": [True, False],
        },
    )

    square_training = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Resize images to square shape instead of aspect ratio "
            "resizing for single image training. For mosaic training, "
            "this resizes single images to square shape first then puts "
            "them on a square canvas.",
            "enum": [True, False],
        },
    )
    seed = fields.Int(
        required=False,
        load_default=42,
        metadata={"description": "Global seed for training."},
    ) 
    
    disable_wandb = fields.Bool(
        required=False,
        load_default=True,
        metadata={"description": "Whether to use WandB for logging."},
    )

    disable_mlflow = fields.Bool(
        required=False,
        load_default=True,
        metadata={"description": "Whether to use WandB for logging."},
    )


    


class PredictArgsSchema(Schema):
    class Meta:
        ordered = True

    input = fields.Field(
        required=True,
        type="file",
        location="form",
        metadata={
            "description": "Input either an image or a video.\n"
            "video must be in the format MP4, AVI, MKV, MOV, WMV, FLV, WebM.\n"
            "Images must be in the format JPEG, PNG, BMP, GIF, TIFF, PPM,"
            "EXR, WebP."
        },
    )

    timestamp = fields.Str(
        required=False,
        load_default=None,
        metadata={
            "description": "Model timestamp to be used for prediction. To see "
            "the available timestamp, please run the get_metadata function. "
            "If no timestamp is given, the model will be loaded from COCO."
        },
    )

    model = fields.Str(
        required=False,
        load_default="fasterrcnn_resnet50_fpn_v2",
        metadata={
            "description": "Please provide the name of the model you want to use "
            "for inference. If you have specified neither timestamp nor model "
            "name, the default model 'fasterrcnn_resnet50_fpn_v2' is loaded.",
            "enum": configs.BACKBONES,
        },
    )

    threshold = fields.Float(
        required=False,
        load_default=0.5,
        metadata={"description": "Detection threshold."},
    )

    imgsz = fields.Int(
        required=False,
        load_default=640,
        metadata={
            "description": "Image size to feed to the network."
        },
    )

    device = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Computation device, default is GPU if GPU is present.",
            "enum": [True, False],
        },
    )

    no_labels = fields.Bool(
        required=False,
        load_default=False,
        metadata={
            "description": "Visualize output only if this argument is passed",
            "enum": [True, False],
        },
    )

    square_img = fields.Bool(
        required=False,
        load_default=True,
        metadata={
            "description": "Whether to use square image resize, else use aspect ratio"
            "resize.",
            "enum": [True, False],
        },
    )

    accept = fields.Str(
        load_default="application/json",
        location="headers",
        validate=validate.OneOf(
            ["application/json", "image/png", "video/mp4"]
        ),
        metadata={
            "description": "Returns a PNG file with detection results or a JSON with"
            "the prediction."
        },
    )


if __name__ == "__main__":
    pass
