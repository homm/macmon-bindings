CMACMON_ZIP_URL := https://github.com/homm/macmon/releases/download/capi-v0.10.0.1/CMacmon.xcframework-v0.10.0.1.zip
CMACMON_ZIP_SHA256 := 8f55541930c8b0eac54c25324997b28c179e6ce8db318473ed1c503a7b626b10
PYTHON_PLATFORM := macosx-11.0-arm64


CMacmon.xcframework:
	tmp_zip="$$(mktemp /tmp/cmacmon.XXXXXX.zip)" && \
	trap 'rm -f "$$tmp_zip"' EXIT && \
	curl -L "$(CMACMON_ZIP_URL)" -o "$$tmp_zip" && \
	echo "$(CMACMON_ZIP_SHA256)  $$tmp_zip" | shasum -a 256 -c - && \
	rm -rf CMacmon.xcframework && \
	unzip -q "$$tmp_zip"


.PHONY: cmacmon
cmacmon: CMacmon.xcframework


.PHONY: python_wheel
python_wheel:
	$(MAKE) -B cmacmon
	pip install "build>=1.4" "delocate>=0.13"
	rm -rf python/dist
	cd python && _PYTHON_HOST_PLATFORM=$(PYTHON_PLATFORM) python -m build --wheel
	python -m delocate.cmd.delocate_wheel --wheel-dir python/wheelhouse python/dist/*.whl
