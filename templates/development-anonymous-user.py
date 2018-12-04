{
    "kind": "Template",
    "apiVersion": "v1",
    "metadata": {
        "name": "workshop-jupyterhub-development-anonymous-user",
        "annotations": {
            "openshift.io/display-name": "Workshop (Development/Anonymous User)"
        }
    },
    "parameters": [
        {
            "name": "PROJECT_NAME",
            "value": "",
            "required": true
        },
        {
            "name": "APPLICATION_NAME",
            "value": "terminals",
            "required": true
        },
        {
            "name": "GIT_REPOSITORY_URL",
            "value": "https://github.com/openshift-labs/workshop-jupyterhub.git",
            "required": true
        },
        {
            "name": "GIT_REPOSITORY_REF",
            "value": "develop",
            "required": true
        },
        {
            "name": "MEMORY_SIZE",
            "value": "512Mi"
        },
        {
            "name": "VOLUME_SIZE",
            "value": "1Gi"
        },
        {
            "name": "IDLE_TIMEOUT",
            "value": "900"
        },
        {
            "name": "MAX_SESSION_AGE",
            "value": "3600"
        },
        {
            "name": "JUPYTERHUB_IMAGE",
            "value": "quay.io/osevg/jupyterhub-quickstart:2.0.1"
        },
        {
            "name": "TERMINAL_IMAGE",
            "value": "quay.io/osevg/workshop-dashboard:master"
        },
        {
            "name": "OC_VERSION",
            "value": ""
        },
        {
            "name": "ODO_VERSION",
            "value": ""
        },
        {
            "name": "KUBECTL_VERSION",
            "value": ""
        },
        {
            "name": "JUPYTERHUB_CONFIG",
            "value": "",
            "required": false
        }
    ],
    "objects": [
        {
            "kind": "ServiceAccount",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-${PROJECT_NAME}-hub",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            }
        },
        {
            "kind": "RoleBinding",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-edit",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "${APPLICATION_NAME}-${PROJECT_NAME}-hub"
                }
            ],
            "roleRef": {
                "name": "edit"
            }
        },
        {
            "kind": "ClusterRoleBinding",
            "apiVersion": "v1",
            "metadata": {
                "name": "${PROJECT_NAME}-${APPLICATION_NAME}-self-provisioner",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "${APPLICATION_NAME}-${PROJECT_NAME}-hub",
                    "namespace": "${PROJECT_NAME}"
                }
            ],
            "roleRef": {
                "name": "self-provisioner"
            }
        },
        {
            "kind": "ImageStream",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-hub-s2i",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "spec": {
                "lookupPolicy": {
                    "local": true
                },
                "tags": [
                    {
                        "name": "latest",
                        "from": {
                            "kind": "DockerImage",
                            "name": "${JUPYTERHUB_IMAGE}"
                        }
                    }
                ]
            }
        },
        {
            "kind": "ImageStream",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-hub-img",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            }
        },

        {
            "kind": "BuildConfig",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-hub-img",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "spec": {
                "triggers": [
                    {
                        "type": "ConfigChange"
                    },
                    {
                        "type": "ImageChange"
                    }
                ],
                "source": {
                    "type": "Git",
                    "git": {
                        "uri": "${GIT_REPOSITORY_URL}",
                        "ref": "${GIT_REPOSITORY_REF}"
                    },
                    "contextDir": "jupyterhub"
                },
                "strategy": {
                    "type": "Source",
                    "sourceStrategy": {
                        "from": {
                            "kind": "ImageStreamTag",
                            "name": "${APPLICATION_NAME}-hub-s2i:latest"
                        }
                    }
                },
                "output": {
                    "to": {
                        "kind": "ImageStreamTag",
                        "name": "${APPLICATION_NAME}-hub-img:latest"
                    }
                }
            }
        },
        {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-cfg",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "data": {
                "jupyterhub_config.py": "${JUPYTERHUB_CONFIG}"
            }
        },
	{
	    "kind": "DeploymentConfig",
	    "apiVersion": "v1",
	    "metadata": {
		"name": "${APPLICATION_NAME}",
		"labels": {
		    "app": "${APPLICATION_NAME}"
		}
	    },
	    "spec": {
		"strategy": {
		    "type": "Recreate"
		},
		"triggers": [
		    {
			"type": "ConfigChange"
		    },
		    {
			"type": "ImageChange",
			"imageChangeParams": {
			    "automatic": true,
			    "containerNames": [
				"spawner"
			    ],
			    "from": {
				"kind": "ImageStreamTag",
				"name": "${APPLICATION_NAME}-hub-img:latest"
			    }
			}
		    }
		],
		"replicas": 1,
		"selector": {
		    "app": "${APPLICATION_NAME}",
		    "deploymentconfig": "${APPLICATION_NAME}"
		},
		"template": {
		    "metadata": {
			"labels": {
			    "app": "${APPLICATION_NAME}",
			    "deploymentconfig": "${APPLICATION_NAME}"
			}
		    },
		    "spec": {
			"serviceAccountName": "${APPLICATION_NAME}-${PROJECT_NAME}-hub",
			"containers": [
			    {
				"name": "spawner",
				"image": "${APPLICATION_NAME}-hub-img:latest",
				"ports": [
				    {
					"containerPort": 8080,
					"protocol": "TCP"
				    }
				],
				"env": [
                                    {
                                        "name": "CONFIGURATION_TYPE",
                                        "value": "anonymous-user"
                                    },
				    {
					"name": "APPLICATION_NAME",
					"value": "${APPLICATION_NAME}"
				    },
				    {
					"name": "MEMORY_SIZE",
					"value": "${MEMORY_SIZE}"
				    },
				    {
					"name": "VOLUME_SIZE",
					"value": "${VOLUME_SIZE}"
				    },
				    {
					"name": "IDLE_TIMEOUT",
					"value": "${IDLE_TIMEOUT}"
				    },
				    {
					"name": "MAX_SESSION_AGE",
					"value": "${MAX_SESSION_AGE}"
				    },
                                    {
                                        "name": "OC_VERSION",
                                        "value": "${OC_VERSION}"
                                    },
                                    {
                                        "name": "ODO_VERSION",
                                        "value": "${ODO_VERSION}"
                                    },
                                    {
                                        "name": "KUBECTL_VERSION",
                                        "value": "${KUBECTL_VERSION}"
                                    }
				],
				"volumeMounts": [
				    {
					"mountPath": "/opt/app-root/data",
					"name": "data"
				    },
				    {
					"name": "config",
					"mountPath": "/opt/app-root/configs"
				    }
				]
			    }
			],
			"volumes": [
			    {
				"name": "data",
				"persistentVolumeClaim": {
				    "claimName": "${APPLICATION_NAME}-hub-data"
				}
			    },
			    {
				"name": "config",
				"configMap": {
				    "name": "${APPLICATION_NAME}-cfg",
				    "defaultMode": 420
				}
			    }
			]
		    }
		}
	    }
	},
	{
	    "apiVersion": "v1",
	    "kind": "PersistentVolumeClaim",
	    "metadata": {
		"name": "${APPLICATION_NAME}-hub-data",
		"labels": {
		    "app": "${APPLICATION_NAME}"
		}
	    },
	    "spec": {
		"accessModes": [
		    "ReadWriteOnce"
		],
		"resources": {
		    "requests": {
			"storage": "1Gi"
		    }
		}
	    }
	},
	{
	    "kind": "Service",
	    "apiVersion": "v1",
	    "metadata": {
		"name": "${APPLICATION_NAME}",
		"labels": {
		    "app": "${APPLICATION_NAME}"
		}
	    },
	    "spec": {
		"ports": [
		    {
			"name": "8080-tcp",
			"protocol": "TCP",
			"port": 8080,
			"targetPort": 8080
		    },
		    {
			"name": "8081-tcp",
			"protocol": "TCP",
			"port": 8081,
			"targetPort": 8081
		    }
		],
		"selector": {
		    "app": "${APPLICATION_NAME}",
		    "deploymentconfig": "${APPLICATION_NAME}"
		}
	    }
	},
	{
	    "kind": "Route",
	    "apiVersion": "v1",
	    "metadata": {
		"name": "${APPLICATION_NAME}",
		"labels": {
		    "app": "${APPLICATION_NAME}"
		}
	    },
	    "spec": {
		"host": "",
		"to": {
		    "kind": "Service",
		    "name": "${APPLICATION_NAME}",
		    "weight": 100
		},
		"port": {
		    "targetPort": "8080-tcp"
		},
		"tls": {
		    "termination": "edge",
		    "insecureEdgeTerminationPolicy": "Redirect"
		}
	    }
	},
        {
            "kind": "ImageStream",
            "apiVersion": "v1",
            "metadata": {
                "name": "${APPLICATION_NAME}-app",
                "labels": {
                    "app": "${APPLICATION_NAME}"
                }
            },
            "spec": {
                "lookupPolicy": {
                    "local": true
                },
                "tags": [
                    {
                        "name": "latest",
                        "from": {
                            "kind": "DockerImage",
                            "name": "${TERMINAL_IMAGE}"
                        }
                    }
                ]
            }
        }
    ]
}

