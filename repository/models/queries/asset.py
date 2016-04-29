# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


ASSET_CLASS = "op:Asset"

ASSET_LIST_ID_NAME = "entity"
ASSET_LIST_EXTRA_IDS = """?source_id_value ?source_id_type"""
ASSET_LIST_EXTRA_QUERY = """
    ?{id_name} op:alsoIdentifiedBy ?alt_id .
            ?alt_id op:id_type ?source_id_type ;
                    op:value ?source_id_value .
"""

ASSET_APPEND_ALSO_IDENTIFIED = """
   {entity_id} op:alsoIdentifiedBy  _:bnode .
  _:bnode{bnodeuuid0} op:id_type {source_id_type} .
  _:bnode{bnodeuuid0} op:value	{source_id_value} .
  _:bnode{bnodeuuid0} rdf:type	op:Id .
"""

# CHANGE THE ASSOCIATED OFFER TO AN ASSET IF THE OFFER REFERS TO IT DIRECTLY
ASSET_ADD_OFFER_DIRECT = '''
INSERT
{{
   {new_offer_id} odrl:target ?s .
}}
WHERE
{{
  ?s rdf:type op:Asset .
  {old_offer_id} odrl:target ?s .
}}
'''

ASSET_GET_POLICIES_FOR_ASSETS = """
SELECT ?{idname}_id_bundle  (GROUP_CONCAT(DISTINCT ?entity_entity; separator='|') as ?ids) (GROUP_CONCAT(DISTINCT ?policy; separator='|') as ?policies)
WHERE
{{
    hint:Query hint:optimizer "Runtime" .

    {subquery}

    BIND (CONCAT(STR(?{idname}_id_type), "#" , STR(?{idname}_id_value)) AS ?{idname}_id_bundle) .

    {{ ?policy odrl:target ?{idname}_entity  . ?policy a {policy_type} . }}
    UNION
    {{ ?policy odrl:target/op:fromSet/op:hasElement ?{idname}_entity . ?policy a {policy_type} . }}

}}
GROUP BY ?{idname}_id_bundle
"""

# UTILITY
ASSET_QUERY_ALL_IDS = '''
PREFIX op: <http://openpermissions.org/ns/op/1.0/>

SELECT ?entity_uri ?source_id_type ?source_id
WHERE
{
  ?entity_uri rdf:type op:Asset ;
           op:alsoIdentifiedBy ?altid .
           ?altid op:id_type ?source_id_type ;
                  op:value ?source_id .
}
'''

ASSET_SELECT_BY_ENTITY_ID = """
SELECT ?{idname}_entity ?{idname}_id_value ?{idname}_id_type {{
    VALUES (?{idname}_id_value) {{
        {idlist}
    }}
    BIND (?{idname}_id_value AS ?{idname}_entity)
    BIND (hub:hub_key AS ?{idname}_id_type)
}}
"""

ASSET_SELECT_BY_SOURCE_ID = """
SELECT ?{idname}_entity  ?{idname}_id_value ?{idname}_id_type {{
    VALUES ( ?{idname}_id_type ?{idname}_id_value) {{
        {idlist}
    }}
    ?alt_id op:value ?{idname}_id_value .
    ?alt_id op:id_type ?{idname}_id_type .
    ?{idname}_entity op:alsoIdentifiedBy ?alt_id .
}}
"""


ASSET_STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {id} (op:alsoIdentifiedBy)? ?s . }} """
