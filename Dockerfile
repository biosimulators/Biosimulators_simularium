FROM python:3.10

ARG VERSION="0.2.6"

LABEL \
    org.opencontainers.image.authors="Alexander Patrie <apatrie@uchc.edu>, BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.title="biosimulators_simularium"
    # org.opencontainers.image.description="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    # org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_simularium" \
    # org.opencontainers.image.vendor="BioSimulators Team" \
    # org.opencontainers.image.licenses="MIT" \
    # base_image="python:3.10" \
    # version="${VERSION}" \
    # about.summary="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    # about.home="https://github.com/biosimulators/Biosimulators_simularium" \
    # about.license_file="https://github.com/biosimulators/Biosimulators/blob/dev/LICENSE.txt" \
    # about.license="MIT" \
    # about.tags="spatial simulations, particle-based simulations, molecular diffusion, surface interactions, chemical reactions, SBML, SED-ML, COMBINE, OMEX, BioSimulators"

RUN apt-get update -y \
    && apt-get install -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install python-libcombine>=0.2.19
RUN pip install .
ENTRYPOINT ["biosimulators-simularium"]
CMD []

# RUN pip install --upgrade pip \
#     && pip install setuptools wheel twine \
#     && python /app/setup.py sdist bdist_wheel \
#     && twine check dist/* \
#     && twine upload dist/*
