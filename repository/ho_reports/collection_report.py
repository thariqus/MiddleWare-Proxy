import logging

from repository.database_configuration.postgres_connection import get_connection

logger = logging.getLogger(__name__)


def fetch_collection_report(filters):
    conditions = ""
    params = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        params["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        params["to_date"] = filters["to_date"]

    if filters.get("customers"):
        conditions += " AND so.customer = ANY(%(customers)s)"
        params["customers"] = filters["customers"]

    if filters.get("sales_orders"):
        conditions += " AND so.name = ANY(%(sales_orders)s)"
        params["sales_orders"] = filters["sales_orders"]

    if filters.get("sales_invoices"):
        conditions += " AND si.name = ANY(%(sales_invoices)s)"
        params["sales_invoices"] = filters["sales_invoices"]

    query = """
        SELECT * FROM (
            SELECT DISTINCT ON(si.name)

                si.posting_date AS date,
                so.custom_site AS site,
                site.site_name AS site_name,
                so.custom_distribution_channel_code AS channel,

                (
                    SELECT STRING_AGG(cmp.mode_of_payment, ', ')
                    FROM "tabCustomer Mode of Payment" cmp
                    WHERE cmp.parent = so.name
                        AND cmp.parent = so.name
                        AND cmp.store_code = so.store_code
                ) AS so_type,

                CASE
                    WHEN si.is_return = 1 THEN si.name
                    ELSE so.name
                END AS so_no,

                cust.customer_type AS customer_type_1,

                (
                    SELECT STRING_AGG(cmp.mode_of_payment,  ', ')
                    FROM "tabCustomer Mode of Payment" cmp
                    WHERE cmp.parent = so.name
                    AND cmp.store_code = so.store_code
                ) AS customer_type_2,

                so.customer AS customer_no,
                so.customer_name AS customer_name,
                cust.customer_group AS customer_group,
                NULL AS document_no,
                so.owner AS biller_id,
                d.driver AS driver_id,
                si.owner AS cashier_id,
                so.advance_paid AS advance_amount,

                COALESCE(si.grant_total, so.net_total) AS sales_amount,

                COALESCE(sir.grant_total, 0) AS sales_return_amount,

                CASE
                    WHEN si.grand_total IS NOT NULL THEN
                        CASE 
                            WHEN sir.name IS NOT NULL
                            THEN si.grand_total + COALESCE(sir.grand_total, 0)
                            ELSE si.grand_total
                        END
                    ELSE so.grand_total
                END AS net_sales_amount,

                GREATEST(
                    CASE
                        when si.name IS NOT NULL
                        THEN COALESCE(si.outstanding_amount, 0)
                        ELSE so.grand_total - COALESCE(so.advance_paid, 0)
                    END,
                    0
                ) AS pending_amount,

                (
                    SELECT STRING_AGG(DISTINCT pe.mode_of_payment, ', ')
                    FROM "tabPayment Entry Reference" per
                    INNER JOIN "tabPayment Entry" pe
                        ON pe.name = per.parent
                        AND pe.store_code = per.store_code
                        AND pe.docstatus = 1
                    WHERE per.reference_name = si.name
                    AND per.store_code = si.store_code
                ) AS mode_of_payment,

                si.status AS status,
                si.name AS clearing_doc_no,
                NULL AS ageing

            FROM "tabSales Order" so

            LEFT JOIN "tabSales Invoice" si
                ON si.custom_sales_order = so.name
                AND si.store_code = so.store_code
                AND si.docstatus = 1

            LEFT JOIN "tabSales Invoice" sir
                ON sir.return_against = si.name
                AND sir.store_code = si.store_code
                AND sir.is_return = 1

            LEFT JOIN "tabDriver Sales Order Details" da
                ON da.sales_order_id = so.name
                AND da.store_code = so.store_code

            LEFT JOIN "tabDriver Assignment" d
                ON d.name = da.parent
                AND d.store_code = da.store_code

            LEFT JOIN "tabSite" site
                ON site.name = so.custom_site
                AND site.store_code = so.store_code

            LEFT JOIN "tabCustomer" cust
                ON cust.name = so.customer
                AND cust.store_code = so.store_code

            WHERE so.docstatus = 1
                AND si.name IS NOT NULL
                {conditions}

            ORDER BY si.name, si.posting_date DESC
        ) report
            ORDER BY report.date DESC
    """.format(conditions = conditions)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
    

    except Exception:
        logger.exception("fetch_collection_report failed (filters = %s)", filters)
        raise