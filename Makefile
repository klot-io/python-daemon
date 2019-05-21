ACCOUNT=klotio
IMAGE=python-daemon
VERSION?=0.1
VOLUMES=-v ${PWD}/subscriptions/:/opt/service/subscriptions/ \
		-v ${PWD}/lib/:/opt/service/lib/ \
		-v ${PWD}/bin/:/opt/service/bin/ \
		-v ${PWD}/test/:/opt/service/test/
ENVIRONMENT=-e SLEEP=0.1 \
			-e CHANNEL=klot.io/base

.PHONY: build shell test run push create update delete

build:
	docker build . -t $(ACCOUNT)/$(IMAGE):$(VERSION)

shell:
	docker run -it $(VOLUMES) $(ENVIRONMENT) $(ACCOUNT)/$(IMAGE):$(VERSION) sh

test:
	docker run -it $(VOLUMES) $(ENVIRONMENT) $(ACCOUNT)/$(IMAGE):$(VERSION) sh -c "coverage run -m unittest discover -v test && coverage report -m --include lib/service.py"

run:
	docker run -it $(VOLUMES) $(ENVIRONMENT) --rm -h $(IMAGE) $(ACCOUNT)/$(IMAGE):$(VERSION)

push:
	docker push $(ACCOUNT)/$(IMAGE):$(VERSION)

install:
	kubectl create -f kubernetes/daemon.yaml

update:
	kubectl replace -f kubernetes/daemon.yaml

remove:
	-kubectl delete -f kubernetes/daemon.yaml

reset: remove install