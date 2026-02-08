With this script you can create the config map from a file:

kubectl -n python-lambda-operator create configmap webhook-python-lambda-operator --dry-run=client --from-file=sync.py -oyaml > webhook-cm.yaml