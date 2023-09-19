FROM ubuntu:latest

ARG VERSION="0.2.0"
ARG SIMULATOR_VERSION="2.72"

LABEL \
    org.opencontainers.image.authors="Alexander Patrie <apatrie@uchc.edu>, BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.title="biosimulators_simularium" \
    org.opencontainers.image.version="${SIMULATOR_VERSION}" \
    org.opencontainers.image.description="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_simularium" \
    org.opencontainers.image.vendor="BioSimulators Team" \
    org.opencontainers.image.licenses="MIT" \
    base_image="ubuntu:latest" \
    version="${VERSION}" \
    software="smoldyn" \
    software.version="${SIMULATOR_VERSION}" \
    about.summary="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    about.home="https://github.com/biosimulators/Biosimulators_simularium" \
    about.license_file="https://github.com/biosimulators/Biosimulators/blob/dev/LICENSE.txt" \
    about.license="MIT" \
    about.tags="spatial simulations, particle-based simulations, molecular diffusion, surface interactions, chemical reactions, SBML, SED-ML, COMBINE, OMEX, BioSimulators"

COPY . /app/
WORKDIR /app

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && pip install --upgrade pip setuptools wheel \
    && pip install .

ENTRYPOINT ["biosimulators-simularium"]
CMD []