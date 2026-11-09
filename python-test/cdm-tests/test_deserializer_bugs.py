import json
from pathlib import Path
from finos.cdm.event.common.TradeState import TradeState
from finos.cdm.product.template.Payout import Payout  

def find(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if v == "NOTIONAL":
                print(f"{path}/{k}")
            find(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            find(v, f"{path}[{i}]")

def test_deserializer_bug_01():
    path = Path(
        "resources/samples/fpml-confirmation-to-trade-state/"
        "fpml-5-13-products-credit-derivatives/cd-ex01-long-asia-corp-fixreg.json"
    )
    
    raw = json.loads(path.read_text())
    
    print("JSON payout keys: ", list(raw['trade']['product']['economicTerms']['payout'][0].keys()))
    print("Payout fields: ", list(Payout.model_fields))
    
    ts = TradeState.rune_deserialize(path.read_text(), validate_model=False)
    p = ts.trade.product.economicTerms.payout[0]
    
    print("Fields actually set: ", p.model_fields_set)
    
    assert not p.model_fields_set, f"Expected empty set, but got {p.model_fields_set}"

from finos.cdm.event.common.TradeState import TradeState 
from finos.cdm.product.template.SettlementPayout import SettlementPayout

def test_deserializer_bug_02():
    print(SettlementPayout.model_fields["underlier"])

from typing import Annotated
from pydantic import TypeAdapter

def test_deserializer_bug_03():
    field = SettlementPayout.model_fields["underlier"]
    print("validators on the field:", field.metadata)

    # Check if metadata exists before using Annotated
    if field.metadata:
        adapter = TypeAdapter(Annotated[field.annotation, *field.metadata])
    else:
        adapter = TypeAdapter(field.annotation)

    samples = {
        "ref only":          {"@ref:scoped": "observable-1"},
        "ref + @type":       {"@type": "cdm.observable.asset.Observable",
                              "@ref:scoped": "observable-1"},
    }
    for name, payload in samples.items():
        try:
            print(name, "->", adapter.validate_python(payload))
        except Exception as e:
            print(name, "-> ERROR:", e)

def test_deserializer_bug_04():
    data = json.load(open("resources/samples/fpml-confirmation-to-trade-state/"
                        "fpml-5-10-incomplete-products-credit-derivatives/cdx-index-option.json"))

    find(data)