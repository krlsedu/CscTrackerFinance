INSERT INTO public.transactions (date, type, value, name, package_name, app_name, text, user_id, last_update, category,
                                 key, copy, request_id, is_installment, installment_id)
select pl.date_sell,
       'income',
       ROUND(((usm.quantity * usm.price) - (pl.quantity * value))::numeric, 2),
       ticker,
       null,
       'B3',
       'Resgate de ' || pl.quantity || ' cotas de ' || s.name || ' no preço de venda de ' || usm.price || ' Reais',
       1,
       usm.date,
       'Resgate',
       pl.id || '_' || usm.id,
       false,
       null,
       'N',
       null
from profit_loss pl,
     stocks s,
     user_stocks_movements usm
where s.id = pl.investment_id
  and usm.investment_id = pl.investment_id
--     and TO_CHAR(usm.date, 'YYYY-MM-DD')::date = date_sell
  and usm.quantity = pl.quantity
  and usm.movement_type = 2
  and not exists (select 1 from transactions where key = pl.id || '_' || usm.id and category = 'Resgate')
order by pl.id desc;

INSERT INTO public.transactions (date, type, value, name, package_name, app_name, text, user_id, last_update, category,
                                 key, copy, request_id, is_installment, installment_id)
select pl.date_sell,
       'income',
       ROUND((pl.quantity * value)::numeric, 4),
       ticker,
       null,
       'B3',
       'Lucro referente a venda de ' || pl.quantity || ' cotas de ' || s.name || ' no preço de venda de ' ||
       usm.price || ' Reais',
       1,
       usm.date,
       'Lucro investimentos',
       pl.id || '_' || usm.id,
       false,
       null,
       'N',
       null
from profit_loss pl,
     stocks s,
     user_stocks_movements usm
where s.id = pl.investment_id
  and usm.investment_id = pl.investment_id
--     and TO_CHAR(usm.date, 'YYYY-MM-DD')::date = date_sell
  and usm.quantity = pl.quantity
  and usm.movement_type = 2
  and pl.value > 0
  and not exists (select 1 from transactions where key = pl.id || '_' || usm.id and category = 'Lucro investimentos')
order by pl.id desc;

INSERT INTO public.transactions (date, type, value, name, package_name, app_name, text, user_id, last_update, category,
                                 key, copy, request_id, is_installment, installment_id)
select pl.date_sell,
       'outcome',
       ROUND((pl.quantity * value)::numeric, 4) * -1,
       ticker,
       null,
       'B3',
       'Prejuízo referente a venda de ' || pl.quantity || ' cotas de ' || s.name || ' no preço de venda de ' ||
       usm.price || ' Reais',
       1,
       usm.date,
       'Prejuízo investimentos',
       pl.id || '_' || usm.id,
       false,
       null,
       'N',
       null
from profit_loss pl,
     stocks s,
     user_stocks_movements usm
where s.id = pl.investment_id
  and usm.investment_id = pl.investment_id
--     and TO_CHAR(usm.date, 'YYYY-MM-DD')::date = date_sell
  and usm.quantity = pl.quantity
  and usm.movement_type = 2
  and pl.value < 0
  and not exists (select 1 from transactions where key = pl.id || '_' || usm.id and category = 'Prejuízo investimentos')
order by pl.id desc;