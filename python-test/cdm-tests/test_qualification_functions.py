import pytest
from pathlib import Path
import builtins

# ==============================================================================
# BULLETPROOF WORKAROUND: Inject ALL missing types into Python's builtins 
# This automatically catches any class the Java generator forgot to import.
# ==============================================================================
import finos._bundle as bundle
for name in dir(bundle):
    # Only grab the generated CDM classes
    if name.startswith("finos_"):
        setattr(builtins, name, getattr(bundle, name))
# ==============================================================================

# Import the TradeState model and the runtime attribute resolver
from finos.cdm.event.common.TradeState import TradeState
from rune.runtime.utils import rune_resolve_attr

# Import the specific generated qualification functions
from finos.cdm.product.qualification.functions.Qualify_AssetClass_Credit import Qualify_AssetClass_Credit
from finos.cdm.product.qualification.functions.Qualify_AssetClass_ForeignExchange import Qualify_AssetClass_ForeignExchange

### Check the rest of AssetClass Qualification 
# Level 1: Asset Class
# Level 2: Product Class
# Level 3: Subproduct Class
# Level 4: Transaction Type

def get_economic_terms(relative_path: str):
    """
    Helper function replicating Java's getEconomicTerms.
    Reads the JSON file, deserializes it into a TradeState, and extracts EconomicTerms.
    """
    base_dir = Path(__file__).parent
    full_path = base_dir / "resources" / "samples" / "fpml-confirmation-to-trade-state" / relative_path
    
    with open(full_path, "r", encoding="utf-8") as f:
        json_data = f.read()
        
    # Deserialize the JSON string using the Pydantic BaseDataClass classmethod
    trade_state = TradeState.rune_deserialize(json_data)
    
    # Extract the EconomicTerms safely handling the Choice Type alias
    economic_terms = rune_resolve_attr(trade_state.trade.product, "economicTerms")
    
    return economic_terms

# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Credit
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="On development")
def test_should_qualify_as_asset_class_credit():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-credit-derivatives/cd-ex01-long-asia-corp-fixreg.json"
    )
    result = Qualify_AssetClass_Credit(economic_terms)
    assert result is True

@pytest.mark.skip(reason="On development")
def test_should_not_qualify_as_asset_class_credit():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-fx-derivatives/fx-ex08-fx-swap.json"
    )
    result = Qualify_AssetClass_Credit(economic_terms)
    assert result is False
# ---------------------------------------------------------------------------
# Test: Qualify Asset Class - Foreign Exchange
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="On development")
def test_should_qualify_as_asset_class_foreign_exchange():
    economic_terms = get_economic_terms(
        "fpml-5-13-products-fx-derivatives/fx-ex08-fx-swap.json"
    )
    result = Qualify_AssetClass_ForeignExchange(economic_terms)
    assert result is True

@pytest.mark.skip(reason="On development")
def test_should_not_qualify_as_asset_class_foreign_exchange():
    economic_terms = get_economic_terms(
        "fpml-5-10-incomplete-products-credit-derivatives/cdx-index-option.json"
    )
    result = Qualify_AssetClass_ForeignExchange(economic_terms)
    assert result is False