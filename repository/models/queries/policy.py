# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


POLICY_CLASS = "op:Policy"
OFFER_CLASS = "odrl:Offer"
AGREEMENT_CLASS = "odrl:Agreement"

OFFER_LIST_EXTRA_IDS = """?title"""
OFFER_LIST_EXTRA_QUERY = """
    OPTIONAL {{ ?{id_name} dcterm:title ?title . }}
"""


ODRL_CONSTRAINT = "odrl:constraint"
ODRL_DUTY = "odrl:duty"
ODRL_PERMISSION = "odrl:permission"
ODRL_PROHIBITION = "odrl:prohibition"
POLICY_ASSIGNER = "odrl:assigner"
POLICY_ASSIGNEE = "odrl:assignee"

OFFER_EXPIRE_PREDICATE = "op:expires"
POLICY_TARGET = "odrl:target"
SET_CLASS = "op:Set"
ASSET_SELECTOR_CLASS = "op:AssetSelector"
SET_HAS_ELEMENT = "op:hasElement"
ASSETSELECTOR_FROMSET = "op:fromSet"
ASSETSELECTOR_COUNT = "op:count"

POLICY_STRUCT = {
  ODRL_PERMISSION: {
    ODRL_DUTY: {ODRL_CONSTRAINT: None,
                POLICY_ASSIGNER: None,
                POLICY_ASSIGNEE: None
                },
    ODRL_CONSTRAINT: None,
    POLICY_ASSIGNER: None,
    POLICY_ASSIGNEE: None
  },
  ODRL_PROHIBITION: {ODRL_CONSTRAINT: None,
                     POLICY_ASSIGNER: None,
                     POLICY_ASSIGNEE: None
                     },
  ODRL_DUTY: {ODRL_CONSTRAINT: None,
              POLICY_ASSIGNER: None,
              POLICY_ASSIGNEE: None
              },
  POLICY_ASSIGNER: None,
  POLICY_ASSIGNEE: None
}


def struct_to_struct_selector(d, p="", s="?"):
    if d is None:
        return s
    r = []
    for k in d.keys():
        r.append(k)
        sk = struct_to_struct_selector(d[k], k+"/", "")
        if len(sk):
            r.append("(" + sk + ")")
    return p+"(%s)" % ("|".join(r))+s


_POLICY_STRUCT_SELECTOR = struct_to_struct_selector(POLICY_STRUCT)

POLICY_STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {{ {id} %s ?s .  }} UNION {{ {id} (%s)/odrl:target ?s . ?s a op:AssetSelector . }}  }} """ % (_POLICY_STRUCT_SELECTOR, _POLICY_STRUCT_SELECTOR)

DUTY_CONSTRAINT_PATH = "(odrl:permission/odrl:duty/odrl:constraint|odrl:duty/odrl:constraint)"
POLICY_METADATA_ATTRIBUTE_MAP = {
    "payAmount": {"query": DUTY_CONSTRAINT_PATH+"/odrl:value", "filters": ["?s odrl:payAmount ?o ."]},
    "host": {"query": DUTY_CONSTRAINT_PATH+"/odrl:value", "filters": ["?s op:host ?o ."]}
}

GET_POLICY_TARGETS = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX op: <http://openpermissions.org/ns/op/1.1/>
PREFIX id: <http://openpermissions.org/ns/id/>

SELECT ?target ?type ?set_id ?max_items ?sel_required
WHERE
{{
    hint:Query hint:optimizer "Runtime" .

    id:{id} odrl:target ?target .
    {{
        BIND (op:Asset as ?type) .
        ?target a ?type .
    }}
    UNION {{
        BIND (op:AssetSelector as ?type) .
        ?target a ?type .
        ?target op:fromSet ?set_id .
        OPTIONAL {{
                 ?target op:count ?max_items .
        }}
        OPTIONAL {{
                 ?target op:selectRequired ?sel_required .
        }}
    }}
}}
"""
