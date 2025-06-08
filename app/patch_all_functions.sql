CREATE FUNCTION public.usp_event_log_add(p_entity_id text, p_event_type_id integer, p_reason_id integer, p_value numeric, p_unit text, p_ts timestamp with time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.event_log (
        entity_id,
        event_type_id,
        reason_id,
        value,
        unit,
        ts,
        inserted_at,
        inserted_by
    ) VALUES (
        p_entity_id,
        p_event_type_id,
        p_reason_id,
        p_value,
        p_unit,
        p_ts,
        NOW(),
        current_user
    );

    RETURN 'Event logged successfully';
END;
$$;


--
CREATE FUNCTION public.usp_textdata_add(x_id_dev character varying, x_dat text, d_ts timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_dat INTEGER;  -- Renamed the variable to avoid ambiguity
    d_crt TIMESTAMP := NOW();
BEGIN
    INSERT INTO TextData (X_ID_DEV, X_DAT, D_TS, D_CRT)
    VALUES (x_id_dev, x_dat, d_ts, d_crt)
    RETURNING I_DAT INTO v_i_dat;

    RETURN v_i_dat::TEXT;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message
END;
$$;


--
CREATE FUNCTION public.usp_textdata_all_by_device(p_x_id_dev character varying) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT TextData.I_DAT, TextData.X_ID_DEV, TextData.X_DAT, TextData.D_TS, TextData.D_CRT
    FROM TextData
    WHERE TextData.X_ID_DEV = p_x_id_dev;
END;
$$;


--
CREATE FUNCTION public.usp_textdata_by_date(p_start_date timestamp without time zone, p_end_date timestamp without time zone) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        TextData.I_DAT AS i_dat, 
        TextData.X_ID_DEV AS x_id_dev, 
        TextData.X_DAT AS x_dat, 
        TextData.D_TS AS d_ts, 
        TextData.D_CRT AS d_crt
    FROM TextData
    WHERE TextData.D_TS BETWEEN p_start_date AND p_end_date;  -- Added table alias here
END;
$$;


--
CREATE FUNCTION public.usp_textdata_by_id(p_id integer) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TextData.I_DAT AS i_dat,
        TextData.X_ID_DEV AS x_id_dev,
        TextData.X_DAT AS x_dat,
        TextData.D_TS AS d_ts,
        TextData.D_CRT AS d_crt
    FROM TextData
    WHERE TextData.I_DAT = p_id;
END;
$$;


--
CREATE FUNCTION public.usp_textdata_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData;
    RETURN 'All records deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


--
CREATE FUNCTION public.usp_textdata_delete_by_device(p_x_id_dev character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData
    WHERE X_ID_DEV = p_x_id_dev;
    
    RETURN 'Records for device deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


--
CREATE FUNCTION public.usp_textdata_delete_by_id(p_i_dat integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData
    WHERE I_DAT = p_i_dat;
    
    RETURN 'Record deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


--
CREATE FUNCTION public.usp_textdata_edit(p_i_dat integer, p_x_id_dev character varying, p_x_dat text, p_d_ts timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE TextData
    SET 
        X_ID_DEV = p_x_id_dev,
        X_DAT = p_x_dat,
        D_TS = p_d_ts
    WHERE I_DAT = p_i_dat;
    
    IF FOUND THEN
        RETURN 'Record updated successfully';
    ELSE
        RETURN 'No record found to update';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return error message if something goes wrong
END;
$$;


--
