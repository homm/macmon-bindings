CMACMON_ZIP_URL := https://github.com/homm/macmon/releases/download/v0.7.2/CMacmon.xcframework-v0.7.2.zip
CMACMON_ZIP_SHA256 := 1cdcbb9bde1c035b1a9b767e7182afa5bc12f0f2472e1938cb7533fa3a70ea4a
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
python_wheel: cmacmon
	pip install "build>=1.4" "delocate>=0.13"
	rm -rf python/dist
	cd python && _PYTHON_HOST_PLATFORM=$(PYTHON_PLATFORM) python -m build --wheel
	python -m delocate.cmd.delocate_wheel --wheel-dir python/wheelhouse python/dist/*.whl
