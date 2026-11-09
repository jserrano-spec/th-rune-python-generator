from pathlib import Path
from rune.runtime.cow import rune_unwrap
from pydantic import BaseModel
import json

# Import the TradeState model and the runtime attribute resolver
from finos.cdm.event.common.TradeState import TradeState
from rune.runtime.utils import rune_resolve_deep_attr

# Import the specific generated qualification functions
from finos.cdm.product.qualification.functions.Qualify_AssetClass_Credit import Qualify_AssetClass_Credit
from finos.cdm.product.qualification.functions.Qualify_AssetClass_ForeignExchange import Qualify_AssetClass_ForeignExchange

### Check the rest of AssetClass Qualification 
# Level 1: Asset Class
# Level 2: Product Class
# Level 3: Subproduct Class
# Level 4: Transaction Type

"""
---MAIN ISSUE---

Expected:
"payout": [
  { "CreditDefaultPayout": { "payerReceiver": {...}, "generalTerms": {...} } },
  { "InterestRatePayout":  { "payerReceiver": {...}, "rateSpecification": {...} } }
]

Found:
"payout": [
  { "@type": "cdm.product.asset.CreditDefaultPayout", "payerReceiver": {...}, "generalTerms": {...} },
  { "@type": "cdm.product.asset.InterestRatePayout",  "payerReceiver": {...}, ... }
]
"""

def get_economic_terms(relative_path: str):
    """
    Helper function replicating Java's getEconomicTerms.
    Reads the JSON file, deserializes it into a TradeState, and extracts EconomicTerms.
    """
    base_dir = Path(__file__).parent
    full_path = base_dir / "resources" / "samples" / "fpml-confirmation-to-trade-state" / relative_path
    
    with open(full_path, "r", encoding="utf-8") as f:
        json_data = f.read()
        
    # Disable strict validation so incomplete FpML samples don't crash Pydantic
    trade_state = TradeState.rune_deserialize(json_data, validate_model=False)
    
    # Extract the EconomicTerms safely handling the Choice Type alias
    economic_terms = rune_resolve_deep_attr(trade_state.trade.product, "economicTerms")
    
    return economic_terms

def beautiful_dump(obj):
    """Recursively converts nested models into plain dictionaries for clean printing."""
    if isinstance(obj, BaseModel):
        # Extract fields, ignoring internal private variables starting with '_'
        return {k: beautiful_dump(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, list):
        return [beautiful_dump(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: beautiful_dump(v) for k, v in obj.items()}
    elif hasattr(obj, 'value'): 
        # Handle Enums cleanly
        return obj.value
    else:
        return obj

# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Credit
# ---------------------------------------------------------------------------
def test_should_qualify_as_asset_class_credit():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-credit-derivatives/cd-ex01-long-asia-corp-fixreg.json"
    )

    raw_terms = rune_unwrap(economic_terms)

    print("\n--- ECONOMIC TERMS ---")
    print(json.dumps(beautiful_dump(raw_terms), indent=4, default=str))
    print("\n ---------------------")

    result = Qualify_AssetClass_Credit(economic_terms)
    assert result is True

def test_should_not_qualify_as_asset_class_credit():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-fx-derivatives/fx-ex08-fx-swap.json"
    )
    result = Qualify_AssetClass_Credit(economic_terms)
    assert result is False
    
# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Foreign Exchange
# ---------------------------------------------------------------------------
def test_should_qualify_as_asset_class_foreign_exchange():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-fx-derivatives/fx-ex08-fx-swap.json"
    )
    result = Qualify_AssetClass_ForeignExchange(economic_terms)
    assert result is True

def test_should_not_qualify_as_asset_class_foreign_exchange():
    economic_terms = get_economic_terms(
        "fpml-5-10-incomplete-products-credit-derivatives/cdx-index-option.json"
    )
    result = Qualify_AssetClass_ForeignExchange(economic_terms)
    assert result is False

# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Commodity
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Equity
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Interest Rate
# ---------------------------------------------------------------------------
