FORMAT: 1A
HOST: https://repo-stage.copyrighthub.org

# Open Permissions Platform Coalition Repository Service
The Repository Service saves entities to a repository.

## Standard error output
On endpoint failure there is a standard way to report errors.
The output should be of the form

| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| errors   | A list of errors          | array  |

### Error
| Property         | Description                                 | Type   | Mandatory |
| :-------         | :----------                                 | :---   | :-------  |
| source           | The name of the service producing the error | string | yes       |
| line             | The line number with the error              | number | no        |
| asset_id_type    | The type of the asset identity              | string | no        |
| message          | A description of the error                  | string | yes       |

# Authorization

This API requires authentication. Where [TOKEN] is indicated in an endpoint header you should supply an OAuth 2.0 access token with the appropriate scope (read, write or delegate).

See [How to Auth](https://github.com/openpermissions/auth-srv/blob/master/documents/markdown/how-to-auth.md)
for details of how to authenticate Hub services.

# Group Repository Service Information

## Repository service information [/v1/repository]

### Retrieve service information [GET]

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | The service information   | object |

##### Service information
| Property     | Description                    | Type   |
| :-------     | :----------                    | :---   |
| service_name | The name of the api service    | string |
| service_id   | The id of the api service      | string |
| version      | The version of the api service | string |


+ Request
    + Headers

            Accept: application/json

+ Response 200 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 200,
                "data": {
                    "service_name": "Open Permissions Platform Coalition Repository Service",
                    "service_id": "c9936d2ae20f11e597309a79f06e9478",
                    "version": "0.1.0"
                }
            }

# Group Capabilities
Capabilities/limitations of the service

## Repository service capabilities [/v1/repository/capabilities]

### Retrieve service capabilities [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | The service capabilities  | object |

##### Service capabilities
| Property        | Description                            | Type   |
| :-------        | :----------                            | :---   |
| max_page_size   | Maximum size of page returned by pager | number |
| request_timeout | Default API request timeout in seconds | number |

+ Request
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)
    + Body

            {
                "status": 200,
                "data": {
                    "max_page_size": 1000,
                    "request_timeout": 60
                }
            }

# Group Assets

## Assets resource [/v1/repository/repositories/{repository_id}/assets]

+ Parameters
    + repository_id: `4e605140414e60514041` (required, string)
        Id of repository to store asset in

### Create an Asset [POST]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input
| Property | Description                | Type   | Mandatory |
| :------- | :----------                | :---   | :-------  |
| body     | Asset in xml or ttl format | string | yes       |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |

+ Request to store valid xml data (application/xml)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            <?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:odrl="http://www.w3.org/ns/odrl/2/"
               xmlns:op="http://openpermissions.org/ns/op/1.1/"
               xmlns:opex="http://openpermissions.org/ns/opex/1.0/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            >
                <rdf:Description rdf:about="http://openpermissions.org/ns/id/10000010">
                    <rdf:type rdf:resource="http://openpermissions.org/ns/op/1.1/Asset"/>
                    <op:alsoIdentifiedBy>
                        <rdf:Description>
                            <op:value rdf:datatype="http://www.w3.org/2001/XMLSchema#string">10000010</op:value>
                            <rdf:type rdf:resource="http://openpermissions.org/ns/op/1.1/Id"/>
                            <op:idtype rdf:resource="http://openpermissions.org/ns/hubid/examplecopictureid"/>
                        </rdf:Description>
                    </op:alsoIdentifiedBy>
                    <opex:explicitOffer rdf:resource="http://openpermissions.org/ns/id/0ffe301"/>
                    <opex:explicitOffer rdf:resource="http://openpermissions.org/ns/id/0ffe302"/>
                </rdf:Description>
            </rdf:RDF>

+ Response 200 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 200
            }


+ Request to store not supported Content-Type data (application/notvalid)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            ...invalid data...

+ Response 415 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 415,
                "errors": [
                    {
                        "source": "repository",
                        "message": "application/notvalid not supported. Must be one of application/xml, text/rdf+n3"
                    }
                ]
            }


+ Request with missing data (application/xml)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body


            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "No data"
                    }
                ]
            }


+ Request invalid xml (application/xml)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            <?xml version="1.0" encoding="UTF-8"?>
            <note>
                <p>
                    badly formed xml
            </note>

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "line": 4,
                        "message": "Badly formed xml"
                    }
                ]
            }

## Asset Resource [/v1/repository/repositories/{repository_id}/assets/{asset_id}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from
    + asset_id (required, string)
        Id for the asset

### Get an Asset [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | Asset in JSON-LD format   | object |


+ Request asset (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "uid": "8245a4e810f441259f7fba6bdd9381d90928",
                    "op:count": 1,
                    "@context": {
                        "duty": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "owl": "http://www.w3.org/2002/07/owl#",
                        "@vocab": "http://www.w3.org/ns/odrl/2/",
                        "target": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "hub": "http://openpermissions.org/ns/hub/",
                        "constraint": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "@language": "en",
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "opex": "http://openpermissions.org/ns/opex/1.0/",
                        "op:alsoIdentifiedBy": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "odrl": "http://www.w3.org/ns/odrl/2/",
                        "prohibition": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "ol": "http://openpermissions.org/ns/op/1.1/",
                        "permission": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "dct": "http://purl.org/dc/terms/",
                        "id": "http://openpermissions.org/ns/id/"
                    },
                    "@id": "id:8245a4e810f441259f7fba6bdd9381d94e86",
                    "@type": [
                        "op:Asset",
                        "op:AssetSelector",
                        "Asset"
                    ],
                    "op:fromSet": {
                        "@id": "id:8245a4e810f441259f7fba6bdd9381d94e86"
                    }
                }
            }

+ Request an offer that does not exist (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "asset not found"
                    }
                ]
            }

## Retrieve Identifiers [/v1/repository/repositories/{repository_id}/assets/identifiers{?from}{?to}{?page}{?page_size}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from
    + from (optional, iso8601 formatted timestamp)
        Beginning of the time window for modified assets are queried for
        + Default: one day before now
    + to (optional, iso8601 formatted timestamp)
        End of the time window for modified assets are queried for
        + Default: now
    + page (optional,integer)
        Page to return
        + Default: 1
    + page_size (optional, integer)
        Number of results to include per-page
        + Default: 1000

### Get identifiers of Assets [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description                                       | Type   |
| :------- | :----------                                       | :---   |
| status   | The status of the request                         | number |
| data     | List of identifiers associated with entity_ids    | array  |
| metadata | Information about the results                     | object |

##### Identifiers
| Property       | Description                               | Type     |
| :-------       | :----------                               | :---     |
| entity_uri     | Uri of the asset                          | uri      |
| source_id      | Source Id of the asset                    | string   |
| source_id_type | Id type of the asset Id                   | string   |
| last_modified  | Timestamp of when asset was last modified | datetime |

##### Metadata
| Property     | Description                                 | Type   |
| :-------     | :----------                                 | :---   |
| service_id   | Id of repository service                    | string |
| result_range | Range of modified timestamps within results | array  |
| query_range  | Query modified range                        | array  |
| next         | URL to next page of results                 | URL    |

#### Pagination

If there is data, the metadata object will contain a `next` attribute which
is the URL for the next page of results. The `next` attribute will be included
even if the next page is empty.

+ Request identifiers in database (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
               "status" : 200,
               "data" : [
                  {
                     "entity_uri" : "http://openpermissions.org/ns/id/5be1aea2ae544c368f161b8f0d225077",
                     "source_id" : "5be1aea2ae544c368f161b8f0d225077",
                     "last_modified" : "2016-03-08T10:54:38+00:00",
                     "source_id_type" : "testcopictureid"
                  },
                  {
                     "entity_uri" : "http://openpermissions.org/ns/id/a94a56c2d2ef42c1a6196d72b68623a0",
                     "source_id_type" : "testcopictureid",
                     "source_id" : "a94a56c2d2ef42c1a6196d72b68623a0",
                     "last_modified" : "2016-03-08T10:54:40+00:00"
                  },
                  {
                     "entity_uri" : "http://openpermissions.org/ns/id/698f1ea3c6a04dfb9c196c8911eda48e",
                     "source_id" : "698f1ea3c6a04dfb9c196c8911eda48e",
                     "last_modified" : "2016-03-08T10:54:42+00:00",
                     "source_id_type" : "testcopictureid"
                  },
                  {
                     "source_id_type" : "testcopictureid",
                     "source_id" : "4fff68a9d66446e6a2d32211f99ed5c3",
                     "last_modified" : "2016-03-08T15:13:32+00:00",
                     "entity_uri" : "http://openpermissions.org/ns/id/4fff68a9d66446e6a2d32211f99ed5c3"
                  },
                  {
                     "last_modified" : "2016-03-08T15:13:34+00:00",
                     "source_id" : "a9ed4e8f84a040c4a664354760169a4d",
                     "source_id_type" : "testcopictureid",
                     "entity_uri" : "http://openpermissions.org/ns/id/a9ed4e8f84a040c4a664354760169a4d"
                  }
               ],
               "metadata" : {
                  "next" : "https://repository0:8004/v1/repository/repositories/0fa220b384014735e04632463c1c3092/assets/identifiers?to=2016-03-08T16%3A07%3A50.891466&from=2016-03-08T15%3A13%3A34%2B00%3A00&page=2&page_size=1000",
                  "service_id" : "0fa220b384014735e04632463c1ba5a9",
                  "query_range" : [
                     "2010-01-01T00:00:00Z",
                     "2016-03-08T16:07:50Z"
                  ],
                  "result_range" : [
                     "2016-03-08T10:54:38+00:00",
                     "2016-03-08T15:13:34+00:00"
                  ]
               }
            }


+ Request returning no results (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status" : 200
                "data" : [],
                "metadata" : {
                    "service_id": "b6c37722ab883f75829ea885980008fe"
                    "result_range" : [],
                    "query_range" : [
                        "2015-01-01T00:00:00",
                        "2016-01-01T00:00:00"
                    ]
                }
            }

+ Request Invalid date (application/json; charset=UTF-8)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 400 (application/json; charset=UTF-8)

    + Body

            {
                "status" : 400,
                "errors" : [
                    {
                        "source" : "repository0",
                        "message" : "Invalid format"
                    }
                ]
            }

## Asset Identifiers [/v1/repository/repositories/{repository_id}/assets/{asset_id}/ids]

+ Parameters
    + repository_id (required, string)
        Id for the repository that the asset belongs to
    + asset_id (required, string)
        Id of the asset to update

### List Identifiers associted with an Asset [GET]


| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | list of Source_id objects | list   |


##### Source Id Object
| Property       | Description        | Type   |
| :-------       | :----------        | :---   |
| source_id_type | The type of the id | string |
| source_id      | The id             | string |

+ Request list source_ids associated with an asset (application/json; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data" : [
                    {
                        "source_id_type": "ISBN",
                        "source_id": "0123456789"
                    },
                    {
                        "source_id_type": "ISNI",
                        "source_id": "0000000121032684"
                    }
                ]
            }



### Add Identifiers to an Asset [POST]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input
| Property | Description                | Type  | Mandatory |
| :------- | :----------                | :---  | :-------  |
| ids      | Array of Source Id objects | array | yes       |

##### Source Id Object
| Property       | Description        | Type   |
| :-------       | :----------        | :---   |
| source_id_type | The type of the id | string |
| source_id      | The id             | string |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |


+ Request add two more ids to an asset (application/json; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "ids": [
                    {
                        "source_id_type": "ISBN",
                        "source_id": "0123456789"
                    },
                    {
                        "source_id_type": "ISNI",
                        "source_id": "0000000121032684"
                    }
                ]
            }

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
            }


+ Request add two more ids to an asset with missing data (application/json; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "ids": [
                    {
                        "source_id": "0123456789"
                    },
                    {
                        "source_id_type": "ISNI"
                    }
                ]
            }

+ Response 400 (application/json; charset=utf-8)

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Missing source_id_type for entry: 1"
                    },
                    {
                        "source": "repository",
                        "message": "Missing source_id for entry: 2"
                    }
                ]
            }


+ Request add two more ids to an asset that does not exist (application/json; charset=utf-8)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "ids": [
                    {
                        "source_id_type": "ISBN",
                        "source_id": "0123456789"
                    },
                    {
                        "source_id_type": "ISNI",
                        "source_id": "0000000121032684"
                    }
                ]
            }

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Asset does not exist"
                    }
                ]
            }

## Offers for Assets [/v1/repository/repositories/{repository_id}/search/offers]

+ Parameters
    + repository_id (required, string)
        Id for the repository to retrieve the asset from

### Query Offers for Assets [POST]

| OAuth Token Scope |
| :----------       |
| read              |

#### Input
Array of source_id_type and source_id value pairs.

| Property       | Description                    | Type   | Mandatory |
| :-------       | :----------                    | :---   | :----     |
| source_id type | The type of the asset identity | string | yes       |
| source_id      | The asset identity             | string | yes       |

#### Output
| Property | Description                     | Type   |
| :------- | :----------                     | :---   |
| status   | The status of the request       | number |
| data     | List of assets and their offers | array  |

Assets not found in database are omitted in response array.

If no assets are found, an empty array is returned.

+ Request offers for assets present in database (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            [
                {
                    "source_id_type": "testcopictureid",
                    "source_id": "100456"
                },
                {
                    "source_id_type": "examplecopictureid",
                    "source_id": "100123"
                }
            ]

+ Response 200 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 200,
                "data": [
                    {
                        "source_id": "44f2add7dcb54fdca996806c5df2d463",
                        "entity_id": "749946384adf460982edafecc9c846c0",
                        "offers": [
                            {
                                "@context": {
                                    "duty": {
                                        "type": "@id",
                                        "@container": "@set"
                                    },
                                    "owl": "http://www.w3.org/2002/07/owl#",
                                    "@vocab": "http://www.w3.org/ns/odrl/2/",
                                    "hub": "http://openpermissions.org/ns/hub/",
                                    "constraint": {
                                        "type": "@id",
                                        "@container": "@set"
                                    },
                                    "dct": "http://purl.org/dc/terms/",
                                    "@language": "en",
                                    "dc": "http://purl.org/dc/elements/1.1/",
                                    "opex": "http://openpermissions.org/ns/opex/1.0/",
                                    "op:alsoIdentifiedBy": {
                                        "type": "@id",
                                        "@container": "@set"
                                    },
                                    "odrl": "http://www.w3.org/ns/odrl/2/",
                                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                    "prohibition": {
                                        "type": "@id",
                                        "@container": "@set"
                                    },
                                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                                    "ol": "http://openpermissions.org/ns/op/1.1/",
                                    "id": "http://openpermissions.org/ns/id/",
                                    "permission": {
                                        "type": "@id",
                                        "@container": "@set"
                                    },
                                    "op:sharedDuties": {
                                        "type": "@id",
                                        "@container": "@set"
                                    }
                                },
                                "@graph": [
                                    {
                                        "operator": {
                                            "@id": "odrl:isPartOf"
                                        },
                                        "@id": "id:6f23907270e84653a7a42507c620cbcb",
                                        "@type": "Constraint",
                                        "spatial": {
                                            "@id": "http://sws.geonames.org/6295630/"
                                        }
                                    },
                                    {
                                        "operator": {
                                            "@id": "odrl:lteq"
                                        },
                                        "post": 1,
                                        "@id": "id:419f292044384dd899283f09a57ed9c5",
                                        "@type": "Constraint"
                                    },
                                    {
                                        "operator": {
                                            "@id": "odrl:lteq"
                                        },
                                        "@id": "id:d21acc37c1434588a8d80aa3fe8fcda2",
                                        "@type": "Constraint",
                                        "unit": {
                                            "@id": "opex:pixel"
                                        },
                                        "height": 400
                                    },
                                    {
                                        "action": {
                                            "@id": "odrl:compensate"
                                        },
                                        "@id": "id:8e6a4945c55346d2beedccbb326dca5a",
                                        "@type": [
                                            "Rule",
                                            "Duty"
                                        ],
                                        "assigner": {
                                            "@id": "id:db36b2edcfef4d9795b06a02f8cbb340"
                                        },
                                        "constraint": [
                                            {
                                                "@id": "id:76d8f96af9634d03ab1f4518f8b526db"
                                            }
                                        ]
                                    },
                                    {
                                        "duty": [
                                            {
                                                "@id": "id:8e6a4945c55346d2beedccbb326dca5a"
                                            }
                                        ],
                                        "profile": "http://openpermissions.org/ns/op/1.1/",
                                        "target": {
                                            "@id": "id:749946384adf460982edafecc9c846c0"
                                        },
                                        "assigner": {
                                            "@id": "id:ce4b8a36ed704cba9837113cac310d34"
                                        },
                                        "permission": [
                                            {
                                                "@id": "id:c30feba3720d42879f184322fa5a8ce3"
                                            }
                                        ],
                                        "dct:created": {
                                            "@type": "xsd:dateTime",
                                            "@value": "2016-03-03T16:28:00+00:00"
                                        },
                                        "dct:modified": {
                                            "@type": "xsd:dateTime",
                                            "@value": "2016-03-03T16:29:00+00:00"
                                        },
                                        "inheritAllowed": false,
                                        "@id": "id:4b7a759eb47c45ae938c58fe8a050129",
                                        "uid": "de23b8280cc4478187b33829bf650ac1",
                                        "op:policyDescription": "This Licence Offer is for the display of a single photograph as 'wallpaper' or similar background on a personal digital device such as a mobile phone, laptop computer or camera roll. The Licence Holder must be an individual (not an organization).",
                                        "type": "offer",
                                        "@type": [
                                            "Asset",
                                            "op:Policy",
                                            "Policy",
                                            "Offer"
                                        ],
                                        "conflict": {
                                            "@id": "odrl:invalid"
                                        },
                                        "undefined": {
                                            "@id": "odrl:invalid"
                                        }
                                    },
                                    {
                                        "action": {
                                            "@id": "odrl:attribute"
                                        },
                                        "@id": "id:83078ef7a45447eb8d62fb8c98a7ba19",
                                        "@type": [
                                            "Rule",
                                            "Duty"
                                        ],
                                        "target": {
                                            "@id": "id:fc6ea20a8ce4447f98d1e0b75b506c0e"
                                        }
                                    },
                                    {
                                        "@id": "id:ce4b8a36ed704cba9837113cac310d34",
                                        "op:reference": {
                                            "@value": ""
                                        },
                                        "@type": "op:Party",
                                        "op:provider": {
                                            "@value": "4225f4774d6874a68565a04130001144"
                                        }
                                    },
                                    {
                                        "operator": {
                                            "@id": "odrl:eq"
                                        },
                                        "@id": "id:76d8f96af9634d03ab1f4518f8b526db",
                                        "@type": "Constraint",
                                        "unit": {
                                            "@id": "http://cvx.iptc.org/iso4217a/GBP"
                                        },
                                        "payAmount": {
                                            "@type": "xsd:decimal",
                                            "@value": "10"
                                        }
                                    },
                                    {
                                        "duty": [
                                            {
                                                "@id": "id:83078ef7a45447eb8d62fb8c98a7ba19"
                                            }
                                        ],
                                        "assigner": {
                                            "@id": "id:db36b2edcfef4d9795b06a02f8cbb340"
                                        },
                                        "constraint": [
                                            {
                                                "@id": "id:e5a97bbe58b341eba012b48380db3bb5"
                                            },
                                            {
                                                "@id": "id:d21acc37c1434588a8d80aa3fe8fcda2"
                                            },
                                            {
                                                "@id": "id:6f23907270e84653a7a42507c620cbcb"
                                            },
                                            {
                                                "@id": "id:419f292044384dd899283f09a57ed9c5"
                                            }
                                        ],
                                        "action": {
                                            "@id": "odrl:display"
                                        },
                                        "@id": "id:c30feba3720d42879f184322fa5a8ce3",
                                        "@type": [
                                            "Permission",
                                            "Rule"
                                        ]
                                    }
                                ]
                            }
                        ],
                        "source_id_type": "testcopictureid",
                    }
                ]
            }


+ Request offers for assets not present in database (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            [
                {
                    "source_id_type": "examplecopictureid",
                    "source_id": "NonExistingIDvalue1"
                },
                {
                    "source_id_type": "examplecopictureid",
                    "source_id": "NonExistingIDvalue2"
                }
            ]

+ Response 200 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 200,
                "data": []
            }

+ Request offers with invalid data (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            ...invalid data...

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "No JSON object could be decoded"
                    }
                ]
            }


+ Request offers with missing data (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body


            {
                "status": "400",
                "errors": [
                    {
                        "source": "repository",
                        "message": "No JSON object could be decoded"
                    }
                ]
            }

# Group Offers

## Offers Resource [/v1/repository/repositories/{repository_id}/offers{?page}{?page_size}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from

### Get Offers [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description                | Type   |
| :------- | :----------                | :---   |
| status   | The status of the request  | number |
| data     | Array of offer descriptors | array  |

##### Offer Descriptor
| Property      | Description                               | Type     |
| :-------      | :----------                               | :---     |
| id            | The id of the offer                       | string   |
| title         | The title of the offer                    | string   |
| last_modified | Timestamp of when offer was last modified | datetime |

+ Parameters
    + page (optional,integer)
        Page to return
        + Default: 1
    + page_size (optional, integer)
        Number of results to include per-page
        + Default: 1000

+ Request identifiers in database (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "status": 200,
                "data": {
                    "offers": [
                        {
                            "id": "3e42a0d123cd4231a64024cc24c4032c",
                            "last_modified": "2016-03-03T16:29:00+00:00",
                            "title": null
                        },
                        {
                            "id": "cce3e4dacd2c4b1ab1ca6acde988ed72",
                            "last_modified": "2016-03-03T16:29:00+00:00",
                            "title": null
                        },
                        {
                            "id": "de459a12aa144952824800a86bc333f2",
                            "last_modified": "2016-03-03T16:29:00+00:00",
                            "title": null
                        }
                    ]
                }
            }

### Create an Offer [POST]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input
| Property | Description                   | Type   | Mandatory |
| :------- | :----------                   | :---   | :-------  |
| body     | The JSON-LD body of the offer | object | yes       |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | Id of new offer           | object |


+ Request create offer (application/ld+json)
    + Headers

            Accept: application/ld+json
            Authorization: Bearer [TOKEN]

    + Body

            {
              "@context": {
                "@language": "en",
                "@vocab": "http://www.w3.org/ns/odrl/2/",
                "constraint": {
                  "@container": "@set",
                  "type": "@id"
                },
                "dc": "http://purl.org/dc/elements/1.1/",
                "dct": "http://purl.org/dc/terms/",
                "duty": {
                  "@container": "@set",
                  "type": "@id"
                },
                "hub": "http://openpermissions.org/ns/hub/",
                "id": "http://openpermissions.org/ns/id/",
                "odrl": "http://www.w3.org/ns/odrl/2/",
                "ol": "http://openpermissions.org/ns/op/1.1/",
                "op:alsoIdentifiedBy": {
                  "@container": "@set",
                  "type": "@id"
                },
                "op:sharedDuties": {
                  "@container": "@set",
                  "type": "@id"
                },
                "opex": "http://openpermissions.org/ns/opex/1.0/",
                "owl": "http://www.w3.org/2002/07/owl#",
                "permission": {
                  "@container": "@set",
                  "type": "@id"
                },
                "prohibition": {
                  "@container": "@set",
                  "type": "@id"
                },
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
              },
              "@graph": [
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d15876c0e",
                  "@type": "dc:Text",
                  "dc:description": "This photograph (c) Test Demo PseudoLtd , all rights reserved."
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d1587",
                  "@type": [
                    "Policy",
                    "op:Policy",
                    "Asset",
                    "Offer"
                  ],
                  "conflict": {
                    "@id": "odrl:invalid"
                  },
                  "dct:created": {
                    "@type": "xsd:dateTime",
                    "@value": "2016-03-03T16:28:00"
                  },
                  "dct:modified": {
                    "@type": "xsd:dateTime",
                    "@value": "2016-03-03T16:29:00"
                  },
                  "duty": [
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d15871293"
                    }
                  ],
                  "inheritAllowed": false,
                  "op:policyDescription": "This Licence Offer is for the display of a single photograph as 'wallpaper' or similar background on a personal digital device such as a mobile phone, laptop computer or camera roll. The Licence Holder must be an individual (not an organization).",
                  "permission": [
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d15877852"
                    }
                  ],
                  "profile": "http://openpermissions.org/ns/op/1.1/",
                  "type": "offer",
                  "uid": "463325e5f3e24d6baffa0e2a813d1587",
                  "undefined": {
                    "@id": "odrl:invalid"
                  }
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d15871293",
                  "@type": [
                    "Rule",
                    "Duty"
                  ],
                  "action": {
                    "@id": "odrl:compensate"
                  },
                  "assigner": {
                    "@id": "hub:TestDemoPseudoLtd"
                  },
                  "constraint": [
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d158719b0"
                    }
                  ]
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d1587f61c",
                  "@type": "Constraint",
                  "operator": {
                    "@id": "odrl:lteq"
                  },
                  "unit": {
                    "@id": "opex:pixel"
                  },
                  "width": 400
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d1587faff",
                  "@type": "Constraint",
                  "height": 400,
                  "operator": {
                    "@id": "odrl:lteq"
                  },
                  "unit": {
                    "@id": "opex:pixel"
                  }
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d1587f7f6",
                  "@type": "Constraint",
                  "operator": {
                    "@id": "odrl:isPartOf"
                  },
                  "spatial": {
                    "@id": "http://sws.geonames.org/6295630/"
                  }
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d15874e86",
                  "@type": [
                    "Asset",
                    "op:AssetSelector",
                    "op:Asset"
                  ],
                  "op:count": 1,
                  "op:fromSet": {
                    "@id": "id:463325e5f3e24d6baffa0e2a813d15874e86"
                  },
                  "uid": "463325e5f3e24d6baffa0e2a813d15870928"
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d158799d5",
                  "@type": [
                    "Rule",
                    "Duty"
                  ],
                  "action": {
                    "@id": "odrl:attribute"
                  },
                  "target": {
                    "@id": "id:fc6ea20a8ce4447f98d1e0b75b506c0e"
                  }
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d15877852",
                  "@type": [
                    "Rule",
                    "Permission"
                  ],
                  "action": {
                    "@id": "odrl:display"
                  },
                  "assigner": {
                    "@id": "hub:TestDemoPseudoLtd"
                  },
                  "constraint": [
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d1587faff"
                    },
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d1587f7f6"
                    },
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d15876f61c"
                    },
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d158707b3"
                    }
                  ],
                  "duty": [
                    {
                      "@id": "id:463325e5f3e24d6baffa0e2a813d158799d5"
                    }
                  ]
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d158719b0",
                  "@type": "Constraint",
                  "operator": {
                    "@id": "odrl:eq"
                  },
                  "payAmount": {
                    "@type": "xsd:decimal",
                    "@value": "10.0"
                  },
                  "unit": {
                    "@id": "http://cvx.iptc.org/iso4217a/GBP"
                  }
                },
                {
                  "@id": "id:463325e5f3e24d6baffa0e2a813d158707b3",
                  "@type": "Constraint",
                  "operator": {
                    "@id": "odrl:lteq"
                  },
                  "post": 1
                }
              ]
            }

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "id": "dce9183a67f4424fb4d18917648eaf80"
                }
            }


+ Request no offer data sent
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "no data found"
                    }
                ]
            }


+ Request invalid offer data sent (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                -- invalid offer --
            }

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "invalid offer"
                    }
                ]
            }

## Offer Resource [/v1/repository/repositories/{repository_id}/offers/{offer_id}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the offer from
    + offer_id (required, string)
        Id for the offer

### Get an Offer [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | Offer in JSON-LD format   | object |


+ Request offer (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                        "@context": {
                            "duty": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "owl": "http://www.w3.org/2002/07/owl#",
                            "@vocab": "http://www.w3.org/ns/odrl/2/",
                            "hub": "http://openpermissions.org/ns/hub/",
                            "constraint": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                            "@language": "en",
                            "op:sharedDuties": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "dc": "http://purl.org/dc/elements/1.1/",
                            "opex": "http://openpermissions.org/ns/opex/1.0/",
                            "op:alsoIdentifiedBy": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "odrl": "http://www.w3.org/ns/odrl/2/",
                            "prohibition": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "xsd": "http://www.w3.org/2001/XMLSchema#",
                            "ol": "http://openpermissions.org/ns/op/1.1/",
                            "permission": {
                                "type": "@id",
                                "@container": "@set"
                            },
                            "dct": "http://purl.org/dc/terms/",
                            "id": "http://openpermissions.org/ns/id/"
                        },
                        "@graph": [
                            {
                                "action": {
                                    "@id": "odrl:attribute"
                                },
                                "@id": "id:ca80d22dc5b24b14bc2ed6c072ef9b04",
                                "@type": [
                                    "Duty",
                                    "Rule"
                                ],
                                "target": {
                                    "@id": "id:fc6ea20a8ce4447f98d1e0b75b506c0e"
                                }
                            },
                            {
                                "operator": {
                                    "@id": "odrl:eq"
                                },
                                "@id": "id:4100344c04784688a6d7b2d3a29a3e4f",
                                "@type": "Constraint",
                                "unit": {
                                    "@id": "http://cvx.iptc.org/iso4217a/GBP"
                                },
                                "payAmount": {
                                    "@type": "xsd:decimal",
                                    "@value": "10"
                                }
                            },
                            {
                                "operator": {
                                    "@id": "odrl:lteq"
                                },
                                "@id": "id:7dad6a7ccc86472dad5abaaf43504693",
                                "@type": "Constraint",
                                "unit": {
                                    "@id": "opex:pixel"
                                },
                                "height": 400
                            },
                            {
                                "op:reference": {
                                    "@value": ""
                                },
                                "@id": "id:ed3a5a3b1ae845268bfcdc60c6ec98bf",
                                "@type": "op:Party",
                                "op:provider": {
                                    "@value": "4225f4774d6874a68565a04130001144"
                                }
                            },
                            {
                                "operator": {
                                    "@id": "odrl:isPartOf"
                                },
                                "@id": "id:5d2eccf3439341618a8185066444ed5d",
                                "@type": "Constraint",
                                "spatial": {
                                    "@id": "http://sws.geonames.org/6295630/"
                                }
                            },
                            {
                                "duty": [
                                    {
                                        "@id": "id:ca80d22dc5b24b14bc2ed6c072ef9b04"
                                    }
                                ],
                                "assigner": {
                                    "@id": "id:fbe6dfb5e0d741589172ffc1b613c546"
                                },
                                "constraint": [
                                    {
                                        "@id": "id:5d2eccf3439341618a8185066444ed5d"
                                    },
                                    {
                                        "@id": "id:5435e1efe9b2440db0c6f3b59faf73d8"
                                    },
                                    {
                                        "@id": "id:7dad6a7ccc86472dad5abaaf43504693"
                                    },
                                    {
                                        "@id": "id:3d21d2101de147e9bf8d408dd4dc2478"
                                    }
                                ],
                                "action": {
                                    "@id": "odrl:display"
                                },
                                "@id": "id:d4663ea44660473bbadf7e3df977aca5",
                                "@type": [
                                    "Permission",
                                    "Rule"
                                ]
                            },
                            {
                                "duty": [
                                    {
                                        "@id": "id:354fb35fa44c4db6800a53760a92394b"
                                    }
                                ],
                                "profile": "http://openpermissions.org/ns/op/1.1/",
                                "uid": "c63ad720fcfa48d88e7f81f65f6e648f",
                                "assigner": {
                                    "@id": "id:ed3a5a3b1ae845268bfcdc60c6ec98bf"
                                },
                                "permission": [
                                    {
                                        "@id": "id:d4663ea44660473bbadf7e3df977aca5"
                                    }
                                ],
                                "dct:modified": {
                                    "@type": "xsd:dateTime",
                                    "@value": "2016-03-03T16:29:00+00:00"
                                },
                                "undefined": {
                                    "@id": "odrl:invalid"
                                },
                                "dct:created": {
                                    "@type": "xsd:dateTime",
                                    "@value": "2016-03-03T16:28:00+00:00"
                                },
                                "inheritAllowed": false,
                                "type": "offer",
                                "@id": "id:97ee637c6b58449aa22105670954e6dc",
                                "@type": [
                                    "Policy",
                                    "op:Policy",
                                    "Asset",
                                    "Offer"
                                ],
                                "conflict": {
                                    "@id": "odrl:invalid"
                                },
                                "op:policyDescription": "This Licence Offer is for the display of a single photograph as 'wallpaper' or similar background on a personal digital device such as a mobile phone, laptop computer or camera roll. The Licence Holder must be an individual (not an organization)."
                            },
                            {
                                "operator": {
                                    "@id": "odrl:lteq"
                                },
                                "post": 1,
                                "@id": "id:5435e1efe9b2440db0c6f3b59faf73d8",
                                "@type": "Constraint"
                            },
                            {
                                "action": {
                                    "@id": "odrl:compensate"
                                },
                                "@id": "id:354fb35fa44c4db6800a53760a92394b",
                                "@type": [
                                    "Duty",
                                    "Rule"
                                ],
                                "assigner": {
                                    "@id": "id:fbe6dfb5e0d741589172ffc1b613c546"
                                },
                                "constraint": [
                                    {
                                        "@id": "id:4100344c04784688a6d7b2d3a29a3e4f"
                                    }
                                ]
                            }
                        ],
                        "repository": {
                            "name": "testco repo",
                            "service": {
                                "organisation_id": "toppco",
                                "name": "repository0",
                                "created_by": "admin",
                                "state": "approved",
                                "location": "https://repository0:8004",
                                "service_type": "repository",
                                "id": "2336d8a9edbd824645e365a4e4c0ee08"
                            },
                            "organisation": {
                                "website": "http://testco.openpermissions.org",
                                "name": "TestCo",
                                "twitter": "DigiCatapult",
                                "id": "testco",
                                "phone": "0300 1233 101",
                                "state": "approved",
                                "address": "Open Permissions Platform Coalition\n101 Euston Road London\nNW1 2RA",
                                "email": "exampleco@openpermissions.org",
                                "description": "A fictional company for testing purposes"
                            },
                            "created_by": "testadmin",
                            "state": "approved",
                            "id": "2336d8a9edbd824645e365a4e4c174b9"
                        }
                    }
                }            }

+ Request an offer that does not exist (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "offer not found"
                    }
                ]
            }

### Update an Offer [PUT]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input

| Property | Description                                | Type     | Mandatory |
| :------- | :----------                                | :---     | :-------  |
| expires  | The datetime the offer should be expired   | datetime | yes       |

#### Output
| Property | Description                        | Type   |
| :------- | :----------                        | :---   |
| status   | The status of the request          | number |
| data     | Offer id and new expires timestamp | object |

+ Request Valid offer update (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "expires": "2015-12-31T12:00:00Z"
            }

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "expires": "1999-12-31T23:59:59Z",
                    "id": "dce9183a67f4424fb4d18917648eaf80"
                }
            }


+ Request Invalid offer update (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "expires": "-- invalid expiry date --"
            }

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Invalid expires"
                    }
                ]
            }


+ Request Update already expired offer (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "expires": "-- offer already has expiry date --"
            }

+ Response 400 (application/json; charset=UTF-8)
    + Headers

            Access-Control-Allow-Origin: *

    + Body

            {
                "status": 400,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Already expired"
                    }
                ]
            }

# Group Agreements

## Agreements Resource [/v1/repository/repositories/{repository_id}/agreements]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the agreement from


### Create an Agreement [POST]

| OAuth Token Scope |
| :----------       |
| write              |


#### Input
| Property  | Description                                                | Mandatory  | Type             |
| :-------  | :----------                                                | :--------  | :---             |
| offer_id | Id of the offer used as base                                | Yes        | string           |
| party_id  | Id of the assignee                                         | No         | string           |
| assets_id | List of assets for which the user request an agreement for | No         | list             |
| metadata  | Metadata associate with the constraints of the agreement   | No         | object           |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | The agreement id          | object |

+ Request agreement (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "offer_id": "b81e7e8a5616411486f7fbe1ec7bbe77",
                "party_id": "2357111317"
            }


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "data": {
                    "id": "53135f6b371e40af80e3b51d223a5640",
                    "assets": [
                        "bbdf7b6d58d44f95bfd624b13aeca489"
                    ]
                }
            }

## Agreement Resource [/v1/repository/repositories/{repository_id}/agreements/{agreement_id}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the agreement from
    + agreement_id (required, string)
        Id for the agreement

### Get an Agreement [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description               | Type   |
| :------- | :----------               | :---   |
| status   | The status of the request | number |
| data     | JSON-LD agreement object  | object |

+ Request agreement (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "@context": {
                        "duty": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "owl": "http://www.w3.org/2002/07/owl#",
                        "@vocab": "http://www.w3.org/ns/odrl/2/",
                        "hub": "http://openpermissions.org/ns/hub/",
                        "constraint": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "@language": "en",
                        "op:sharedDuties": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "opex": "http://openpermissions.org/ns/opex/1.0/",
                        "op:alsoIdentifiedBy": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "odrl": "http://www.w3.org/ns/odrl/2/",
                        "prohibition": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "ol": "http://openpermissions.org/ns/op/1.1/",
                        "permission": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "dct": "http://purl.org/dc/terms/",
                        "id": "http://openpermissions.org/ns/id/"
                    },
                    "@graph": [
                    {
                        "operator": {
                            "@id": "odrl:eq"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f19b0",
                        "@type": "Constraint",
                        "unit": {
                            "@id": "http://cvx.iptc.org/iso4217a/GBP"
                        },
                        "payAmount": {
                            "@type": "xsd:decimal",
                            "@value": "10"
                        }
                    },
                    {
                        "operator": {
                            "@id": "odrl:lteq"
                        },
                        "post": 1,
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f07b3",
                        "@type": "Constraint"
                    },
                    {
                        "duty": [
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f99d5"
                        }
                        ],
                        "assigner": {
                            "@id": "hub:TestDemoPseudoLtd"
                        },
                        "constraint": [
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f07b3"
                        },
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844ff7f6"
                        },
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f6f61c"
                        },
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844ffaff"
                        }
                        ],
                        "action": {
                            "@id": "odrl:display"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f7852",
                        "@type": [
                            "Permission",
                        "Rule"
                        ]
                    },
                    {
                        "action": {
                            "@id": "odrl:attribute"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f99d5",
                        "@type": [
                            "Duty",
                        "Rule"
                        ],
                        "target": {
                            "@id": "id:fc6ea20a8ce4447f98d1e0b75b506c0e"
                        }
                    },
                    {
                        "operator": {
                            "@id": "odrl:isPartOf"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844ff7f6",
                        "@type": "Constraint",
                        "spatial": {
                            "@id": "http://sws.geonames.org/6295630/"
                        }
                    },
                    {
                        "duty": [
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f1293"
                        }
                        ],
                        "profile": "http://openpermissions.org/ns/op/1.1/",
                        "type": "offer",
                        "dct:references": {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f"
                        },
                        "permission": [
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f7852"
                        }
                        ],
                        "dct:modified": {
                            "@type": "xsd:dateTime",
                            "@value": "2016-03-03T16:29:00+00:00"
                        },
                        "undefined": {
                            "@id": "odrl:invalid"
                        },
                        "dct:created": {
                            "@type": "xsd:dateTime",
                            "@value": "2016-03-03T16:28:00+00:00"
                        },
                        "inheritAllowed": false,
                        "dct:dateAccepted": {
                            "@type": "xsd:dateTime",
                            "@value": "2016-03-17T12:18:05+00:00"
                        },
                        "target": {
                            "@id": "id:3edbbbf0aa3f4b0cb5cb5e46c96ae456"
                        },
                        "uid": "86ff1f0e224e497b8f8c05ae1181844f",
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f",
                        "@type": [
                            "hub:2357111317",
                            "Policy",
                            "Agreement",
                            "Asset",
                            "op:Policy",
                            "Offer"
                        ],
                        "conflict": {
                            "@id": "odrl:prohibit"
                        },
                        "op:policyDescription": "This Licence Offer is for the display of a single photograph as 'wallpaper' or similar background on a personal digital device such as a mobile phone, laptop computer or camera roll. The Licence Holder must be an individual (not an organization)."
                    },
                    {
                        "operator": {
                            "@id": "odrl:lteq"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844ffaff",
                        "@type": "Constraint",
                        "unit": {
                            "@id": "opex:pixel"
                        },
                        "height": 400
                    },
                    {
                        "action": {
                            "@id": "odrl:compensate"
                        },
                        "@id": "id:86ff1f0e224e497b8f8c05ae1181844f1293",
                        "@type": [
                            "Duty",
                        "Rule"
                        ],
                        "assigner": {
                            "@id": "hub:TestDemoPseudoLtd"
                        },
                        "constraint": [
                        {
                            "@id": "id:86ff1f0e224e497b8f8c05ae1181844f19b0"
                        }
                        ]
                    }
                    ]
                }
            }

+ Request an agreement that does not exist (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Agreement agreement_id not found"
                    }
                ]
            }


## Agreement coverage Resource [/v1/repository/repositories/{repository_id}/agreements/{agreement_id}/coverage{?asset_ids}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the agreement from
    + agreement_id (required, string)
        Id for the agreement
    + asset_ids (required, string)
        Comma separated list of asset IDs

### Query if an Agreement covers specific Assets [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description                                                   | Type   |
| :------- | :--------------------------------------------------------     | :---   |
| status   | The status of the request                                     | number |
| data     | List of asset ids that are confirmed covered by the agreement | object |

+ Request agreement coverage (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "covered_by_agreement":[
                        "03351b2c87424db5bf368ffcb35b8670"
                    ]
                }
            }

+ Request agreement coverage - none of the asset suggested is covered by the agreement (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "covered_by_agreement": []
                }
            }


+ Request an agreement that does not exist (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "Agreement agreement_id not found"
                    }
                ]
            }


# Group Sets

## Sets Resource [/v1/repository/repositories/{repository_id}/sets{?page}{?page_size}]

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from

### Get Sets [GET]

| OAuth Token Scope |
| :----------       |
| read              |

#### Output
| Property | Description                | Type   |
| :------- | :----------                | :---   |
| status   | The status of the request  | number |
| data     | Array of set descriptors   | array  |

##### Set descriptors
| Property      | Description                               | Type     |
| :-------      | :----------                               | :---     |
| set_id        | The id of the set                         | string   |
| title         | Title of the set                          | string   |
| last_modified | Timestamp of when set was last modified   | datetime |

+ Parameters
    + page (optional,integer)
        Page to return
        + Default: 1
    + page_size (optional, integer)
        Number of results to include per-page
        + Default: 1000

+ Request list sets available (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "status": 200,
                "data": {
                    "sets": [
                            {
                                "last_modified": "2016-04-07T15:20:34.626000+00:00",
                                "id": "4a1e60e6f36541bb9e69b6a38f4d16d8",
                                "title": "new set created on 2016-04-07T15:20:34.503736"
                            },
                            {
                                "last_modified": "2016-04-07T15:20:35.917000+00:00",
                                "id": "cf5bc370294146ddbde54e6efbbca0c3",
                                "title": "new set created on 2016-04-07T15:20:35.741384"
                            },
                            {
                                "last_modified": "2016-04-07T15:20:37.018000+00:00",
                                "id": "3b1101bb4122484d98084c252a6f8899",
                                "title": "new set created on 2016-04-07T15:20:36.931635"
                            }
                    ]
                }
            }

### Create a Set [POST]

| OAuth Token Scope |
| :----------       |
| write             |

#### Input
| Property | Description                   | Type   | Mandatory |
| :------- | :----------                   | :---   | :-------  |
| title    | The title of the set          | string | no        |

#### Output
| Property        | Description               | Type   |
| :-------        | :----------               | :---   |
| status          | The status of the request | number |
| data            | Id of the new set         | object |

+ Request create a set (application/ld+json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "id": "dce9183a67f4424fb4d18917648eaf80"
                }
            }

## Set Resource [/v1/repository/repositories/{repository_id}/sets/{set_id}]

Allows to get information about a specific asset set.

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from
    + set_id (required, string)
        Id for the set considered


### Get a Set [GET]

| OAuth Token Scope  |
| :----------        |
| read               |


#### Output
| Property        | Description                                        | Type   |
| :-------        | :----------                                        | :---   |
| status          | The status of the request                          | number |
| data            | JSON-LD data represening the set                   | object |



+ Request retrieve a set description (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                "status": 200,
                "data": {
                    "dcterm:modified": {
                        "@type": "xsd:dateTime",
                        "@value": "2016-04-07T14:27:21.872000+00:00"
                    },
                    "op:hasElement": [
                        {
                            "@id": "id:38b0a6f155484c17833bf8f8e62eb937"
                        },
                        {
                            "@id": "id:75cbc300403f4a47b2ba47cd08371b24"
                        },
                        {
                            "@id": "id:0a8249d3c7f84538a45604f56d30b1d1"
                        },
                        {
                            "@id": "id:c2b68a5ad4d54eea98119d52602c7cae"
                        },
                        {
                            "@id": "id:f034982313634b618e94f7b3b67e1db9"
                        },
                        {
                            "@id": "id:0d24aa45b4d14204bca99dee5a8d437f"
                        },
                        {
                            "@id": "id:76d066def2d0446cbadd459459db4ccd"
                        },
                        {
                            "@id": "id:3723d43fa71749bba2939c11bc07d3a3"
                        },
                        {
                            "@id": "id:f70d8be3d2ce489f95fbccd132ccaa10"
                        },
                        {
                            "@id": "id:c1cc4b8b4a9c4e04a3d258f60e1fcb1a"
                        }
                    ],
                    "dcterm:title": {
                        "@value": "new set created on 2016-04-07T14:27:21.770422"
                    },
                    "@context": {
                        "duty": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "owl": "http://www.w3.org/2002/07/owl#",
                        "@vocab": "http://www.w3.org/ns/odrl/2/",
                        "target": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "hub": "http://openpermissions.org/ns/hub/",
                        "constraint": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "@language": "en",
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "opex": "http://openpermissions.org/ns/opex/1.0/",
                        "op:alsoIdentifiedBy": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "odrl": "http://www.w3.org/ns/odrl/2/",
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "prohibition": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "ol": "http://openpermissions.org/ns/op/1.1/",
                        "permission": {
                            "type": "@id",
                            "@container": "@set"
                        },
                        "dcterm": "http://purl.org/dc/terms/",
                        "id": "http://openpermissions.org/ns/id/"
                    },
                    "@id": "id:32cc52c126a94d5aa8bd6cc3e2c1f6a5",
                    "@type": "op:Set"
                }
            }


+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "asset not found"
                    }
                ]
            }

## Set Assets Resource [/v1/repository/repositories/{repository_id}/sets/{set_id}/assets{?page}{?page_size}]

Allows to manage which asset belong to a set

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from
    + set_id (required, string)
        Id for the set considered

### Get the Assets in a Set [GET]

Retrieve in paginated way the list of assets belonging to a set


| OAuth Token Scope  |
| :----------        |
| read               |


#### Output
| Property        | Description                                              | Type   |
| :-------        | :----------                                              | :---   |
| status          | The status of the request                                | number |
| data            | The asset-list results                                   | Object |

#### Asset-list results
| Property        | Description                                              | Type   |
| :-------        | :----------                                              | :---   |
| assets          | The list of the assets in being returned                 | object |

+ Parameters
    + page (optional,integer)
        Page to return
        + Default: 1
    + page_size (optional, integer)
        Number of results to include per-page
        + Default: 1000

+ Request retrieve the list of the assets in a set in a paginated way (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "data": {
                    "assets": [
                        "0152d116136d46958bfc00f261ea2f12",
                        "2170fc49b4d54635a31a346bc26d896d",
                        "290376a4eeb140d7b88e60363876e613",
                        "36cd8fbb5100478f9f80cb6665b3608e",
                        "37c81160325d49fba0f0adfcccec34a8",
                        "3b61775c5b374925be0a7eec3fbf7ccd",
                        "3f1feaaa514a42b09f843c4411e5ade6",
                        "787ce91c8f73426296bbf95be69eaed6",
                        "9d5abfb4aece4507ab495b87e6110c3c",
                        "b5f743dc7dab44f89ffc19a719b736bb",
                        "b7ec7d487f6042f6aed2938d083dbbec",
                        "c560ea62994d45b18a9d8dd097153032",
                        "cdafbb383d9b471183e2fa2a6ceafa17",
                        "eddd4e56c4e548b189cd88e477d80ac4",
                        "efc475bc24554e7faf06c8ab58ca7994",
                        "fa7c33f201e042c6b1f41882d14c2002"
                    ]
                }
            }


+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

### Update Assets in a Set [POST]

Explicitly define all the assets in a set.

| OAuth Token Scope  |
| :----------        |
| write              |


#### Input
| Property | Description                                | Type   | Mandatory |
| :------- | :----------                                | :---   | :-------  |
| assets   | The list of assets to be submitted         | string | yes        |

#### Output
| Property        | Description               | Type   |
| :-------        | :----------               | :---   |
| status          | The status of the request | number |


+ Request update the list of assets (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

    + Body

            {
                    "assets": [
                        "0152d116136d46958bfc00f261ea2f12",
                        "2170fc49b4d54635a31a346bc26d896d",
                        "290376a4eeb140d7b88e60363876e613",
                        "36cd8fbb5100478f9f80cb6665b3608e",
                        "37c81160325d49fba0f0adfcccec34a8",
                        "3b61775c5b374925be0a7eec3fbf7ccd",
                        "3f1feaaa514a42b09f843c4411e5ade6",
                        "787ce91c8f73426296bbf95be69eaed6",
                        "9d5abfb4aece4507ab495b87e6110c3c",
                        "b5f743dc7dab44f89ffc19a719b736bb",
                        "b7ec7d487f6042f6aed2938d083dbbec",
                        "c560ea62994d45b18a9d8dd097153032",
                        "cdafbb383d9b471183e2fa2a6ceafa17",
                        "eddd4e56c4e548b189cd88e477d80ac4",
                        "efc475bc24554e7faf06c8ab58ca7994",
                        "fa7c33f201e042c6b1f41882d14c2002"
                    ]
            }

+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200
            }


+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

### Remove all the Assets from a Set [DELETE]

Remove all the the assets from a set

| OAuth Token Scope  |
| :----------        |
| write              |


#### Output
| Property        | Description               | Type   |
| :-------        | :----------               | :---   |
| status          | The status of the request | number |


+ Request delete associations of all assets with the set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
            }

+ Request remove assets from an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

## Set Asset Resource [/v1/repository/repositories/{repository_id}/sets/{set_id}/assets/{asset_id}]

Manages the relation of single asset with an asset set

+ Parameters
    + repository_id (required, string)
        Id for the repository to get the asset from
    + set_id (required, string)
        Id for the set considered
    + asset_id (required, string)
        Id for the asset considered


### Query if a single Asset is part a Set [GET]

| OAuth Token Scope  |
| :----------        |
| read               |


#### Output
| Property        | Description                                      | Type    |
| :-------        | :----------                                      | :---    |
| status          | The status of the request                        | number  |
| is_member       | Indicated if an asset is member of a set         | boolean |


+ Request check if an asset is part of a set (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200,
                "is_member": true
            }

+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

+ Request query for an unresolvable asset (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "asset <id> not found"
                    }
                ]
            }

+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

+ Request query for an unresolvable asset (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "asset <id> not found"
                    }
                ]
            }

### Add a single Asset to a Set [POST]

| OAuth Token Scope  |
| :----------        |
| write              |


#### Output
| Property        | Description               | Type    |
| :-------        | :----------               | :---    |
| status          | Status of query           | integer |



+ Request connect an asset to a set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200
            }


### Remove a single Asset from a Set [DELETE]

| OAuth Token Scope  |
| :----------        |
| write              |


#### Output
| Property        | Description               | Type    |
| :-------        | :----------               | :---    |
| status          | Status of query           | integer |


+ Request disconnect an asset from a set (application/json)

    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]


+ Response 200 (application/json; charset=UTF-8)

    + Body

            {
                "status": 200
            }


+ Request query for an unresolvable set (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "set <id> not found"
                    }
                ]
            }

+ Request query for an unresolvable asset (application/json)
    + Headers

            Accept: application/json
            Authorization: Bearer [TOKEN]

+ Response 404 (application/json; charset=UTF-8)

    + Body

            {
                "status": 404,
                "errors": [
                    {
                        "source": "repository",
                        "message": "asset <id> not found"
                    }
                ]
            }
