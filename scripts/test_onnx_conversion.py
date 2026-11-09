
from pathlib import Path
import xgboost as xgb
import onnx
import onnxmltools

from onnxmltools.convert.common.data_types import FloatTensorType

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR / "ml" / "saved_models" / "xgboost_demand_model.json"
)

OUTPUT_PATH = (
    BASE_DIR / "ml" / "saved_models" / "conversion_test.onnx"
)

print("\nSMARTPERISH - ONNX COMPATIBILITY TEST")
print("=" * 50)

model = xgb.XGBRegressor()
model.load_model(str(MODEL_PATH))

booster = model.get_booster()

original_names = booster.feature_names
original_types = booster.feature_types

print("Original features:", original_names)
print("Feature types:", original_types)

try:
    # Create a separate booster copy
    test_booster = booster.copy()

    # Rename features only in the conversion copy
    test_booster.feature_names = [
        f"f{i}" for i in range(len(original_names))
    ]

    test_booster.feature_types = ["float"] * len(original_names)

    initial_types = [
        ("input", FloatTensorType([None, len(original_names)]))
    ]

    print("\nAttempting conversion...")

    onnx_model = onnxmltools.convert_xgboost(
        test_booster,
        initial_types=initial_types,
        target_opset=15
    )

    onnx.checker.check_model(onnx_model)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    onnxmltools.utils.save_model(
        onnx_model,
        str(OUTPUT_PATH)
    )

    print("\nCONVERSION SUCCESSFUL!")
    print("Saved:", OUTPUT_PATH)

except Exception as error:
    print("\nCONVERSION FAILED")
    print("Error:", type(error).__name__, str(error))

    print("\nOriginal model remains unchanged.")

# Verify original model metadata remains intact
print("\nOriginal model feature names preserved:",
      model.get_booster().feature_names == original_names)

print("Original model feature types preserved:",
      model.get_booster().feature_types == original_types)
