FROM python:3.10-slim-buster

ARG VERSION="0.2.0"
ARG SIMULATOR_VERSION="2.72"

LABEL \
    org.opencontainers.image.authors="Alexander Patrie <apatrie@uchc.edu>, BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.title="biosimulators_simularium" \
    org.opencontainers.image.version="${SIMULATOR_VERSION}" \
    org.opencontainers.image.description="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    org.opencontainers.image.source="https://github.com/biosimulators/Biosimulators_tellurium" \
    org.opencontainers.image.vendor="BioSimulators Team" \
    org.opencontainers.image.licenses="MIT" \
    base_image="python:3.10-slim-buster" \
    version="${VERSION}" \
    software="smoldyn" \
    software.version="${SIMULATOR_VERSION}" \
    about.summary="A Python-based tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format" \
    about.home="https://github.com/biosimulators/Biosimulators_simularium" \
    about.documentation="https://tellurium.readthedocs.io/" \
    about.license_file="https://github.com/biosimulators/Biosimulators/blob/dev/LICENSE.txt" \
    about.license="MIT" \
    about.tags="spatial simulations, particle-based simulations, molecular diffusion, surface interactions, chemical reactions, SBML, SED-ML, COMBINE, OMEX, BioSimulators" \

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install smoldyn \
    && pip install . \
    && rm -rf /root/.cache/pip/

ENTRYPOINT ["biosimulators-simularium"]
CMD []