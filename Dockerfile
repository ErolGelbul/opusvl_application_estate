FROM odoo:16

COPY ./custom-addons/estate /mnt/extra-addons/estate

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/estate \
    && chmod -R 775 /mnt/extra-addons/estate
USER odoo
