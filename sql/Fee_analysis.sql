-- 1.사업자별 전체 평균 요금
select
	operator,
	AVG(price_per_kwh) AS avg_price
from charging_fees
Group By operator
Order By avg_price;

-- 2.회원 요금 사업자별 비교
select 
	operator,
	ROUND(Avg(price_per_kwh),2) AS avg_member_price
From charging_fees
where customer_type = 'member'
Group by operator
Order by avg_member_price;

-- 3.비회원 요금 사업자별 비교
select 
	operator,
	ROUND(Avg(price_per_kwh),2) AS avg_non_member_price
From charging_fees
where customer_type = 'non_member'
Group by operator
Order by avg_non_member_price;

-- 4.회원 vs 비회원 비교
select 
	operator,

	Round(
		AVG(CASE
			when customer_type = 'member'
			then price_per_kwh
		End),
		2) AS member_price,
		
	Round(
		AVG(CASE
			When customer_type = 'non_member'
			then price_per_kwh
		End),2) AS non_member_price,

	Round(
		Avg(Case
			when customer_type = 'non_member'
			then price_per_kwh
		End)
		-
		Avg(Case
			when customer_type = 'member'
			then price_per_kwh
		End),
		2) AS price_difference


From charging_fees
Group by operator
Order by price_difference DESC;
	
-- 5.급속 vs 완속 비교
Select 
	charger_type,
	Round(Avg(price_per_kwh),2) AS avg_price
From charging_fees
where customer_type = 'member'
Group By charger_type
Order By avg_price;


select 
	customer_type, 
	Round(
		Avg(Case
			when charger_type = 'slow'
			then price_per_kwh
		end),2) As slow_price,

	Round(
		Avg(Case
			when charger_type = 'fast'
			then price_per_kwh
		end),2 ) As fast_price,

	Round(
		Avg(case 
			when charger_type = 'fast'
			then price_per_kwh
		End)
		-
		Avg(case
			when charger_type = 'slow'
			then price_per_kwh
		End),
		2) As price_difference

FROM charging_fees

WHERE customer_type IN ('member', 'non_member')

GROUP BY customer_type

ORDER BY customer_type;

SELECT
    operator,
    customer_type,
    charger_type,
    COUNT(*) AS row_count,
    ROUND(AVG(price_per_kwh), 2) AS avg_price
FROM charging_fees
WHERE customer_type IN ('member', 'non_member')
GROUP BY operator, customer_type, charger_type
ORDER BY customer_type, operator, charger_type;



select 
	operator,
	customer_type, 
	Round(
		Avg(Case
			when charger_type = 'slow'
			then price_per_kwh
		end),2) As slow_price,

	Round(
		Avg(Case
			when charger_type = 'fast'
			then price_per_kwh
		end),2 ) As fast_price,

	Round(
		Avg(case 
			when charger_type = 'fast'
			then price_per_kwh
		End)
		-
		Avg(case
			when charger_type = 'slow'
			then price_per_kwh
		End),
		2) As price_difference

FROM charging_fees

WHERE customer_type IN ('member', 'non_member')

GROUP BY customer_type, operator

ORDER BY customer_type, operator;

-- 5.출력구간(power_band)별 요금 분석

select
	operator, power_band

From charging_fees
Group By operator, power_band
order by operator, power_band;

SELECT
    CASE
        WHEN power_band IN ('100-199kw', '100_199kw')
            THEN '100_199kw'
        ELSE power_band
    END AS standardized_power_band,
    COUNT(*) AS row_count
FROM charging_fees
GROUP BY standardized_power_band
ORDER BY standardized_power_band;






WITH standardized AS (
    SELECT
        operator,

        CASE
            WHEN power_band IN ('100-199kw', '100_199kw')
                THEN '100_199kw'
            ELSE power_band
        END AS power_band_std,

        customer_type,
        price_per_kwh

    FROM charging_fees
)

SELECT
    operator,
    power_band_std,

    ROUND(
        AVG(CASE
            WHEN customer_type = 'member'
            THEN price_per_kwh
        END),
        2
    ) AS member_price,

    ROUND(
        AVG(CASE
            WHEN customer_type = 'non_member'
            THEN price_per_kwh
        END),
        2
    ) AS non_member_price

FROM standardized

WHERE power_band_std IS NOT NULL

GROUP BY
    operator,
    power_band_std

ORDER BY
    power_band_std,
    member_price;

-- 6. 구독제/프라임 회원 요금 분석
SELECT
    operator,
    customer_type,
    COUNT(*) AS row_count,
    ROUND(AVG(price_per_kwh), 2) AS avg_price
FROM charging_fees
WHERE customer_type IN ('subscription', 'prime_member')
GROUP BY operator, customer_type
ORDER BY operator, customer_type;


SELECT
    operator,

    ROUND(
        AVG(CASE
            WHEN customer_type = 'member'
            THEN price_per_kwh
        END),
        2
    ) AS member_price,

    ROUND(
        AVG(CASE
            WHEN customer_type IN ('subscription', 'prime_member')
            THEN price_per_kwh
        END),
        2
    ) AS discount_price,

    ROUND(
        AVG(CASE
            WHEN customer_type = 'member'
            THEN price_per_kwh
        END)
        -
        AVG(CASE
            WHEN customer_type IN ('subscription', 'prime_member')
            THEN price_per_kwh
        END),
        2
    ) AS discount_per_kwh,

    ROUND(
        (
            AVG(CASE
                WHEN customer_type = 'member'
                THEN price_per_kwh
            END)
            -
            AVG(CASE
                WHEN customer_type IN ('subscription', 'prime_member')
                THEN price_per_kwh
            END)
        )
        /
        AVG(CASE
            WHEN customer_type = 'member'
            THEN price_per_kwh
        END)
        * 100,
        2
    ) AS discount_percent

FROM charging_fees

WHERE operator IN ('E-pit', 'EVSIS', 'SK일렉링크')

GROUP BY operator
ORDER BY discount_percent DESC;

SELECT
    operator,
    plan_name,
    power_band,
    price_per_kwh,
    monthly_fee_krw,
    quota_kwh
FROM charging_fees
WHERE customer_type IN ('subscription', 'prime_member')
ORDER BY operator, plan_name, power_band;

with member_avg As (
	select
		operator,
		AVG(price_per_kwh) AS member_price
	From charging_fees
	where customer_type = 'member'
	group by operator
)

SELECT
    c.operator,
    c.plan_name,
    c.power_band,
    ROUND(m.member_price, 2) AS member_price,
    c.price_per_kwh AS discount_price,

    ROUND(
        m.member_price - c.price_per_kwh,
        2
    ) AS saving_per_kwh,

    ROUND(
        (m.member_price - c.price_per_kwh)
        / m.member_price * 100,
        2
    ) AS discount_percent,

    c.monthly_fee_krw,
    c.quota_kwh

FROM charging_fees c
JOIN member_avg m
    ON c.operator = m.operator

WHERE c.customer_type IN ('subscription', 'prime_member')

ORDER BY
    c.operator,
    c.plan_name,
    c.power_band;

-- Key Insights
-- 1. SK일렉링크: 낮은 회원가 + 높은 비회원 할증
-- 2. EVSIS / E-pit: 구독, prime을 통한 충성고객 할인
-- 3. 기후에너지환경부: 회원/비회원 가격 차이가 없는 benchmark 성격