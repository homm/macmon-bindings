CMACMON_ZIP_URL := https://github.com/homm/macmon/releases/download/v0.7.0/CMacmon.xcframework-v0.7.0.zip
CMACMON_ZIP_SHA256 := ce002405e52c2706be5ead3d1756591ba4de76aad91428c3bd578dd98b639697
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
