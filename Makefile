ENV=-e APCA_API_KEY_ID -e APCA_API_SECRET_KEY

build:
	docker build -t junalgo .

run:
	docker run --rm -v $(CURDIR):/work $(ENV) junalgo

debug:
	docker run --rm -v $(CURDIR):/work $(ENV) -it junalgo bash
