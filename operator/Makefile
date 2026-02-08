PWD := ${CURDIR}
ADDITIONAL_BUILD_ARGUMENTS?=""

PKG		:= metacontroller
API_GROUPS := metacontroller/v1alpha1

CODE_GENERATOR_VERSION="v0.24.3"

all: generate_crds

.PHONY: generate_crds
generate_crds:
	@echo "+ Generating crds"
	@go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest
	@controller-gen +crd:generateEmbeddedObjectMeta=true +paths="./api/..." +output:crd:stdout > v1/crdv1.yaml

.PHONY: cm
cm:
	@echo "+ Generate webhook-cm.yaml"
	@kubectl -n python-lambda-operator create configmap webhook-python-lambda-operator --dry-run=client --from-file=sync.py -oyaml > webhook-cm.yaml

.PHONY: install
install:
	@echo "+ Installing metacontroller"
	@kubectl apply -f v1/crdv1.yaml
	@kubectl apply -f webhook-cm.yaml
	@kubectl apply -f operator.yaml