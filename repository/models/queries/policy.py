# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# PREDICATE MAPPING
POLICY_CLASS = "op:Policy"
OFFER_CLASS = "odrl:Offer"
AGREEMENT_CLASS = "odrl:Agreement"

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


# Used in conjunction with GENERIC_LIST query.
# :param id_name: name of the variable for the id
# :returns title: Title of offer
OFFER_LIST_EXTRA_IDS = """?title"""
OFFER_LIST_EXTRA_QUERY = """
    OPTIONAL {{ ?{id_name} dcterm:title ?title . }}
"""


# Used by GENERIC_GET to identify the structure of a policy object
# the structure is representing here by indicating the predicates
# that can occur at different level of the policy object and lead
# to a subobject.
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
    """
    help function that constructs the sparl path used by the STRUCT query
    based on previous description of the policy structure
    :param d: data structure
    :param p: path prefix (internal parameter used in recursion)
    :param s: suffix to be added to the path (internal parameter used in recursion)
    :return: sparql path
    """
    if d is None:
        return s
    r = []
    for k in d.keys():
        r.append(k)
        sk = struct_to_struct_selector(d[k], k+"/", "")
        if len(sk):
            r.append("(" + sk + ")")
    return p+"(%s)" % ("|".join(r))+s


# Used by GENERIC_GET
# Returns the policy and also get the target if is an asset selector as we will want to return this target
# as part of the policy in this case.
# :params id: id of element belonging to policy
# :params %s: Policy struct as a SPARQL path (generated from POLICY_STRUCT)
_POLICY_STRUCT_SPARQLPATH = struct_to_struct_selector(POLICY_STRUCT)
POLICY_STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {{ {id} %s ?s .  }} UNION {{ {id} (%s)/odrl:target ?s . ?s a op:AssetSelector . }}  }} """ % (_POLICY_STRUCT_SPARQLPATH, _POLICY_STRUCT_SPARQLPATH)


# The two following queries are  used when transforming offers in agreements
# to record how the assignee claim to have satisfy the duty required by the permissions
# NOTE: this is assuming that there only one duty of each type.
# NOTE: DUTY_CONSTRAINT_PATH is formated for set_attr to work
# and should be read as "(odrl:permission/odrl:duty/odrl:constraint)|(odrl:duty/odrl:constraint)"
DUTY_CONSTRAINT_PATH = "(odrl:permission/odrl:duty/odrl:constraint|odrl:duty/odrl:constraint)"
POLICY_METADATA_ATTRIBUTE_MAP = {
    "payAmount": {"query": DUTY_CONSTRAINT_PATH+"/odrl:value", "filters": ["?s odrl:payAmount ?o ."]},
    "host": {"query": DUTY_CONSTRAINT_PATH+"/odrl:value", "filters": ["?s op:host ?o ."]}
}


# Returns a list of directly identified asset or asset selector that the policy refers to
# NOTE: set_id, max_items and sel_required are used when transforming an offer into
# and agreement to understand if the assets referenced by the user
# are covered by the policy
#
# :param id: Id of policy
#
# :returns target: asset or asset selector that the policy refers to
# :returns type: asset or asset selector that the policy refers to
# :returns set_id: (optional) Id of set if target is asset selector
# :returns max_items: (optional) Maximum number of items that can be used if target is asset selector
# :returns sel_required: (optional) Whether selection is required if target is asset selector
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
