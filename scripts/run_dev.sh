# SPDX-FileCopyrightText: 2022 CERT.at GmbH <https://cert.at>
# SPDX-License-Identifier: AGPL-3.0-or-later

# This is a development-only running script, never use on production

uvicorn intelmq_api.main:app --reload
