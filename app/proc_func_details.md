# Stored Procedures and Functions in ParcoRTLSMaint

> **Note**: Routines with the `usp_` prefix are labeled as `PROCEDURE` in this output but are defined as `FUNCTION` in the database, based on naming convention.

 CREATE OR REPLACE FUNCTION public.postgres_fdw_disconnect(text)       +
  RETURNS boolean                                                      +
  LANGUAGE c                                                           +
  PARALLEL RESTRICTED STRICT                                           +
 AS '$libdir/postgres_fdw', $function$postgres_fdw_disconnect$function$+
 

Name: postgres_fdw_disconnect\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: FUNCTION in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.postgres_fdw_disconnect_all()           +
  RETURNS boolean                                                          +
  LANGUAGE c                                                               +
  PARALLEL RESTRICTED STRICT                                               +
 AS '$libdir/postgres_fdw', $function$postgres_fdw_disconnect_all$function$+
 

Name: postgres_fdw_disconnect_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: FUNCTION in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.postgres_fdw_get_connections(OUT server_name text, OUT valid boolean)+
  RETURNS SETOF record                                                                                  +
  LANGUAGE c                                                                                            +
  PARALLEL RESTRICTED STRICT                                                                            +
 AS '$libdir/postgres_fdw', $function$postgres_fdw_get_connections$function$                            +
 

Name: postgres_fdw_get_connections\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: FUNCTION in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.postgres_fdw_handler()           +
  RETURNS fdw_handler                                               +
  LANGUAGE c                                                        +
  STRICT                                                            +
 AS '$libdir/postgres_fdw', $function$postgres_fdw_handler$function$+
 

Name: postgres_fdw_handler\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: FUNCTION in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.postgres_fdw_validator(text[], oid)+
  RETURNS void                                                        +
  LANGUAGE c                                                          +
  STRICT                                                              +
 AS '$libdir/postgres_fdw', $function$postgres_fdw_validator$function$+
 

Name: postgres_fdw_validator\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: FUNCTION in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_add(p_device_id integer, p_entity_id integer, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone DEFAULT NULL::timestamp without time zone)+
  RETURNS text                                                                                                                                                                                                                                  +
  LANGUAGE plpgsql                                                                                                                                                                                                                              +
 AS $function$                                                                                                                                                                                                                                  +
 BEGIN                                                                                                                                                                                                                                          +
     INSERT INTO deviceassmts (                                                                                                                                                                                                                 +
         device_id,                                                                                                                                                                                                                             +
         entity_id,                                                                                                                                                                                                                             +
         reason_id,                                                                                                                                                                                                                             +
         start_date,                                                                                                                                                                                                                            +
         end_date                                                                                                                                                                                                                               +
     )                                                                                                                                                                                                                                          +
     VALUES (                                                                                                                                                                                                                                   +
         p_device_id,                                                                                                                                                                                                                           +
         p_entity_id,                                                                                                                                                                                                                           +
         p_reason_id,                                                                                                                                                                                                                           +
         p_start_date,                                                                                                                                                                                                                          +
         p_end_date                                                                                                                                                                                                                             +
     );                                                                                                                                                                                                                                         +
                                                                                                                                                                                                                                                +
     RETURN 'Assignment added successfully';                                                                                                                                                                                                    +
 EXCEPTION                                                                                                                                                                                                                                      +
     WHEN OTHERS THEN                                                                                                                                                                                                                           +
         RETURN SQLERRM;                                                                                                                                                                                                                        +
 END;                                                                                                                                                                                                                                           +
 $function$                                                                                                                                                                                                                                     +
 

Name: usp_assign_dev_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_add(p_device_id character varying, p_entity_id character varying, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone DEFAULT NULL::timestamp without time zone)+
  RETURNS text                                                                                                                                                                                                                                                      +
  LANGUAGE plpgsql                                                                                                                                                                                                                                                  +
 AS $function$                                                                                                                                                                                                                                                      +
 BEGIN                                                                                                                                                                                                                                                              +
     INSERT INTO deviceassmts (                                                                                                                                                                                                                                     +
         x_id_dev,                                                                                                                                                                                                                                                  +
         x_id_ent,                                                                                                                                                                                                                                                  +
         i_rsn,                                                                                                                                                                                                                                                     +
         d_asn_bgn,                                                                                                                                                                                                                                                 +
         d_asn_end                                                                                                                                                                                                                                                  +
     )                                                                                                                                                                                                                                                              +
     VALUES (                                                                                                                                                                                                                                                       +
         p_device_id,                                                                                                                                                                                                                                               +
         p_entity_id,                                                                                                                                                                                                                                               +
         p_reason_id,                                                                                                                                                                                                                                               +
         p_start_date,                                                                                                                                                                                                                                              +
         p_end_date                                                                                                                                                                                                                                                 +
     );                                                                                                                                                                                                                                                             +
                                                                                                                                                                                                                                                                    +
     RETURN 'Assignment added successfully';                                                                                                                                                                                                                        +
 EXCEPTION                                                                                                                                                                                                                                                          +
     WHEN OTHERS THEN                                                                                                                                                                                                                                               +
         RETURN SQLERRM;                                                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                                                               +
 $function$                                                                                                                                                                                                                                                         +
 

Name: usp_assign_dev_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_delete(p_asn_dev integer)+
  RETURNS text                                                             +
  LANGUAGE plpgsql                                                         +
 AS $function$                                                             +
 BEGIN                                                                     +
     UPDATE deviceassmts                                                   +
     SET d_asn_end = NOW()                                                 +
     WHERE i_asn_dev = p_asn_dev;                                          +
                                                                           +
     IF FOUND THEN                                                         +
         RETURN 'Assignment end date updated successfully';                +
     ELSE                                                                  +
         RETURN 'No matching record found';                                +
     END IF;                                                               +
 EXCEPTION                                                                 +
     WHEN OTHERS THEN                                                      +
         RETURN SQLERRM;                                                   +
 END;                                                                      +
 $function$                                                                +
 

Name: usp_assign_dev_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_delete_all()  +
  RETURNS text                                                  +
  LANGUAGE plpgsql                                              +
 AS $function$                                                  +
 BEGIN                                                          +
     UPDATE deviceassmts                                        +
     SET d_asn_end = NOW()                                      +
     WHERE d_asn_end IS NULL;                                   +
                                                                +
     IF FOUND THEN                                              +
         RETURN 'All assignment end dates updated successfully';+
     ELSE                                                       +
         RETURN 'No open assignments found';                    +
     END IF;                                                    +
 EXCEPTION                                                      +
     WHEN OTHERS THEN                                           +
         RETURN SQLERRM;                                        +
 END;                                                           +
 $function$                                                     +
 

Name: usp_assign_dev_delete_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_delete_all_by_ent(p_entity_id character varying)+
  RETURNS text                                                                                    +
  LANGUAGE plpgsql                                                                                +
 AS $function$                                                                                    +
 BEGIN                                                                                            +
     DELETE FROM deviceassmts                                                                     +
     WHERE x_id_ent = p_entity_id;                                                                +
                                                                                                  +
     IF FOUND THEN                                                                                +
         RETURN 'All assignments for the entity deleted successfully';                            +
     ELSE                                                                                         +
         RETURN 'No assignments found for the entity';                                            +
     END IF;                                                                                      +
 EXCEPTION                                                                                        +
     WHEN OTHERS THEN                                                                             +
         RETURN SQLERRM;                                                                          +
 END;                                                                                             +
 $function$                                                                                       +
 

Name: usp_assign_dev_delete_all_by_ent\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_edit(p_asn_dev integer, p_device_id character varying, p_entity_id character varying, p_reason_id integer)+
  RETURNS text                                                                                                                                              +
  LANGUAGE plpgsql                                                                                                                                          +
 AS $function$                                                                                                                                              +
 BEGIN                                                                                                                                                      +
     UPDATE deviceassmts                                                                                                                                    +
     SET                                                                                                                                                    +
         x_id_dev = p_device_id,                                                                                                                            +
         x_id_ent = p_entity_id,                                                                                                                            +
         i_rsn = p_reason_id                                                                                                                                +
     WHERE i_asn_dev = p_asn_dev;                                                                                                                           +
                                                                                                                                                            +
     IF FOUND THEN                                                                                                                                          +
         RETURN 'Assignment updated successfully';                                                                                                          +
     ELSE                                                                                                                                                   +
         RETURN 'No matching assignment found';                                                                                                             +
     END IF;                                                                                                                                                +
 EXCEPTION                                                                                                                                                  +
     WHEN OTHERS THEN                                                                                                                                       +
         RETURN SQLERRM;                                                                                                                                    +
 END;                                                                                                                                                       +
 $function$                                                                                                                                                 +
 

Name: usp_assign_dev_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_end(p_asn_dev integer)+
  RETURNS text                                                          +
  LANGUAGE plpgsql                                                      +
 AS $function$                                                          +
 BEGIN                                                                  +
     UPDATE deviceassmts                                                +
     SET d_asn_end = NOW()                                              +
     WHERE i_asn_dev = p_asn_dev AND d_asn_end IS NULL;                 +
                                                                        +
     IF FOUND THEN                                                      +
         RETURN 'Assignment ended successfully';                        +
     ELSE                                                               +
         RETURN 'No open assignment found for the given ID';            +
     END IF;                                                            +
 EXCEPTION                                                              +
     WHEN OTHERS THEN                                                   +
         RETURN SQLERRM;                                                +
 END;                                                                   +
 $function$                                                             +
 

Name: usp_assign_dev_end\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_end_all()+
  RETURNS text                                             +
  LANGUAGE plpgsql                                         +
 AS $function$                                             +
 BEGIN                                                     +
     UPDATE deviceassmts                                   +
     SET d_asn_end = NOW()                                 +
     WHERE d_asn_end IS NULL;                              +
                                                           +
     IF FOUND THEN                                         +
         RETURN 'All open assignments ended successfully'; +
     ELSE                                                  +
         RETURN 'No open assignments found';               +
     END IF;                                               +
 EXCEPTION                                                 +
     WHEN OTHERS THEN                                      +
         RETURN SQLERRM;                                   +
 END;                                                      +
 $function$                                                +
 

Name: usp_assign_dev_end_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_list(p_f_end boolean)                                                                                                                                         +
  RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                              +
 AS $function$                                                                                                                                                                                                  +
 BEGIN                                                                                                                                                                                                          +
     IF p_f_end THEN                                                                                                                                                                                            +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn;                                                                                                                                                            +
     ELSE                                                                                                                                                                                                       +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.d_asn_end IS NULL;                                                                                                                                                                               +
     END IF;                                                                                                                                                                                                    +
 END;                                                                                                                                                                                                           +
 $function$                                                                                                                                                                                                     +
 

Name: usp_assign_dev_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_list_by_entity(p_entity_id character varying, p_f_end boolean)                                                                                                +
  RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                              +
 AS $function$                                                                                                                                                                                                  +
 BEGIN                                                                                                                                                                                                          +
     IF p_f_end THEN                                                                                                                                                                                            +
         -- Include all assignments, even those with an end date                                                                                                                                                +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.x_id_ent = p_entity_id;                                                                                                                                                                          +
     ELSE                                                                                                                                                                                                       +
         -- Only include assignments that have not ended                                                                                                                                                        +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.x_id_ent = p_entity_id AND d.d_asn_end IS NULL;                                                                                                                                                  +
     END IF;                                                                                                                                                                                                    +
 END;                                                                                                                                                                                                           +
 $function$                                                                                                                                                                                                     +
 

Name: usp_assign_dev_list_by_entity\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_list_by_id(p_device_id character varying, p_f_end boolean)                                                                                                    +
  RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                              +
 AS $function$                                                                                                                                                                                                  +
 BEGIN                                                                                                                                                                                                          +
     IF p_f_end THEN                                                                                                                                                                                            +
         -- Include all assignments for the given device, even those with an end date                                                                                                                           +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.x_id_dev = p_device_id;                                                                                                                                                                          +
     ELSE                                                                                                                                                                                                       +
         -- Only include assignments that have not ended                                                                                                                                                        +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.x_id_dev = p_device_id AND d.d_asn_end IS NULL;                                                                                                                                                  +
     END IF;                                                                                                                                                                                                    +
 END;                                                                                                                                                                                                           +
 $function$                                                                                                                                                                                                     +
 

Name: usp_assign_dev_list_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_dev_list_by_reason(p_reason_id integer, p_f_end boolean)                                                                                                          +
  RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                              +
 AS $function$                                                                                                                                                                                                  +
 BEGIN                                                                                                                                                                                                          +
     IF p_f_end THEN                                                                                                                                                                                            +
         -- Include all assignments with the specified reason, even those with an end date                                                                                                                      +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.i_rsn = p_reason_id;                                                                                                                                                                             +
     ELSE                                                                                                                                                                                                       +
         -- Only include active assignments with the specified reason                                                                                                                                           +
         RETURN QUERY                                                                                                                                                                                           +
         SELECT                                                                                                                                                                                                 +
             d.i_asn_dev,                                                                                                                                                                                       +
             d.x_id_dev,                                                                                                                                                                                        +
             d.x_id_ent,                                                                                                                                                                                        +
             d.d_asn_bgn,                                                                                                                                                                                       +
             d.d_asn_end,                                                                                                                                                                                       +
             d.i_rsn,                                                                                                                                                                                           +
             r.x_rsn                                                                                                                                                                                            +
         FROM                                                                                                                                                                                                   +
             deviceassmts d                                                                                                                                                                                     +
         LEFT JOIN                                                                                                                                                                                              +
             tlkassmtreasons r ON d.i_rsn = r.i_rsn                                                                                                                                                             +
         WHERE                                                                                                                                                                                                  +
             d.i_rsn = p_reason_id AND d.d_asn_end IS NULL;                                                                                                                                                     +
     END IF;                                                                                                                                                                                                    +
 END;                                                                                                                                                                                                           +
 $function$                                                                                                                                                                                                     +
 

Name: usp_assign_dev_list_by_reason\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_add(p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer)+
  RETURNS integer                                                                                                                    +
  LANGUAGE plpgsql                                                                                                                   +
 AS $function$                                                                                                                       +
 DECLARE                                                                                                                             +
     v_i_asn_ent INTEGER;                                                                                                            +
 BEGIN                                                                                                                               +
     IF p_i_rsn = -1 THEN                                                                                                            +
         INSERT INTO entityassmts (x_id_pnt, x_id_chd, d_ent_asn_bgn)                                                                +
         VALUES (p_x_id_pnt, p_x_id_chd, NOW())                                                                                      +
         RETURNING i_asn_ent INTO v_i_asn_ent;                                                                                       +
     ELSE                                                                                                                            +
         INSERT INTO entityassmts (x_id_pnt, x_id_chd, i_rsn, d_ent_asn_bgn)                                                         +
         VALUES (p_x_id_pnt, p_x_id_chd, p_i_rsn, NOW())                                                                             +
         RETURNING i_asn_ent INTO v_i_asn_ent;                                                                                       +
     END IF;                                                                                                                         +
                                                                                                                                     +
     RETURN v_i_asn_ent;                                                                                                             +
                                                                                                                                     +
 EXCEPTION                                                                                                                           +
     WHEN OTHERS THEN                                                                                                                +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                                           +
         RETURN -1;                                                                                                                  +
 END;                                                                                                                                +
 $function$                                                                                                                          +
 

Name: usp_assign_entity_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_delete(p_i_asn_ent integer)+
  RETURNS integer                                                               +
  LANGUAGE plpgsql                                                              +
 AS $function$                                                                  +
 BEGIN                                                                          +
     DELETE FROM entityassmts                                                   +
     WHERE i_asn_ent = p_i_asn_ent;                                             +
                                                                                +
     IF FOUND THEN                                                              +
         RETURN 0;  -- Success                                                  +
     ELSE                                                                       +
         RETURN 1;  -- No matching record found                                 +
     END IF;                                                                    +
                                                                                +
 EXCEPTION                                                                      +
     WHEN OTHERS THEN                                                           +
         RAISE NOTICE 'Error: %', SQLERRM;                                      +
         RETURN -1;  -- Error occurred                                          +
 END;                                                                           +
 $function$                                                                     +
 

Name: usp_assign_entity_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_delete_all(p_x_id_ent character varying)+
  RETURNS integer                                                                            +
  LANGUAGE plpgsql                                                                           +
 AS $function$                                                                               +
 BEGIN                                                                                       +
     DELETE FROM entityassmts                                                                +
     WHERE x_id_pnt = p_x_id_ent OR x_id_chd = p_x_id_ent;                                   +
                                                                                             +
     IF FOUND THEN                                                                           +
         RETURN 0;  -- Success                                                               +
     ELSE                                                                                    +
         RETURN 1;  -- No records found                                                      +
     END IF;                                                                                 +
                                                                                             +
 EXCEPTION                                                                                   +
     WHEN OTHERS THEN                                                                        +
         RAISE NOTICE 'Error: %', SQLERRM;                                                   +
         RETURN -1;  -- Error occurred                                                       +
 END;                                                                                        +
 $function$                                                                                  +
 

Name: usp_assign_entity_delete_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_edit(p_i_asn_ent integer, p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer)+
  RETURNS integer                                                                                                                                          +
  LANGUAGE plpgsql                                                                                                                                         +
 AS $function$                                                                                                                                             +
 BEGIN                                                                                                                                                     +
     IF p_i_rsn = -1 THEN                                                                                                                                  +
         UPDATE entityassmts                                                                                                                               +
         SET                                                                                                                                               +
             x_id_pnt = p_x_id_pnt,                                                                                                                        +
             x_id_chd = p_x_id_chd,                                                                                                                        +
             i_rsn = NULL                                                                                                                                  +
         WHERE i_asn_ent = p_i_asn_ent;                                                                                                                    +
     ELSE                                                                                                                                                  +
         UPDATE entityassmts                                                                                                                               +
         SET                                                                                                                                               +
             x_id_pnt = p_x_id_pnt,                                                                                                                        +
             x_id_chd = p_x_id_chd,                                                                                                                        +
             i_rsn = p_i_rsn                                                                                                                               +
         WHERE i_asn_ent = p_i_asn_ent;                                                                                                                    +
     END IF;                                                                                                                                               +
                                                                                                                                                           +
     IF FOUND THEN                                                                                                                                         +
         RETURN 0;  -- Success                                                                                                                             +
     ELSE                                                                                                                                                  +
         RETURN 1;  -- No matching record found                                                                                                            +
     END IF;                                                                                                                                               +
                                                                                                                                                           +
 EXCEPTION                                                                                                                                                 +
     WHEN OTHERS THEN                                                                                                                                      +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                                                                 +
         RETURN -1;  -- Error occurred                                                                                                                     +
 END;                                                                                                                                                      +
 $function$                                                                                                                                                +
 

Name: usp_assign_entity_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_end(p_i_asn_ent integer)+
  RETURNS integer                                                            +
  LANGUAGE plpgsql                                                           +
 AS $function$                                                               +
 BEGIN                                                                       +
     UPDATE entityassmts                                                     +
     SET d_ent_asn_end = NOW()                                               +
     WHERE i_asn_ent = p_i_asn_ent;                                          +
                                                                             +
     IF FOUND THEN                                                           +
         RETURN 0;  -- Success                                               +
     ELSE                                                                    +
         RETURN 1;  -- No matching record found                              +
     END IF;                                                                 +
                                                                             +
 EXCEPTION                                                                   +
     WHEN OTHERS THEN                                                        +
         RAISE NOTICE 'Error: %', SQLERRM;                                   +
         RETURN -1;  -- Error occurred                                       +
 END;                                                                        +
 $function$                                                                  +
 

Name: usp_assign_entity_end\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_end_all(p_x_id_ent character varying)+
  RETURNS integer                                                                         +
  LANGUAGE plpgsql                                                                        +
 AS $function$                                                                            +
 BEGIN                                                                                    +
     UPDATE entityassmts                                                                  +
     SET d_ent_asn_end = NOW()                                                            +
     WHERE x_id_pnt = p_x_id_ent OR x_id_chd = p_x_id_ent;                                +
                                                                                          +
     IF FOUND THEN                                                                        +
         RETURN 0;  -- Success: Assignments ended for specified entity                    +
     ELSE                                                                                 +
         RETURN 1;  -- No matching assignments found                                      +
     END IF;                                                                              +
                                                                                          +
 EXCEPTION                                                                                +
     WHEN OTHERS THEN                                                                     +
         RAISE NOTICE 'Error: %', SQLERRM;                                                +
         RETURN -1;  -- Error occurred                                                    +
 END;                                                                                     +
 $function$                                                                               +
 

Name: usp_assign_entity_end_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list(p_f_end boolean)                                                                                                                                              +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     IF p_f_end THEN                                                                                                                                                                                                    +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn;                                                                                                                                                                    +
     ELSE                                                                                                                                                                                                               +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.d_ent_asn_end IS NULL;                                                                                                                                                                                   +
     END IF;                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list_by_child(p_x_id_chd character varying, p_f_end boolean)                                                                                                       +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     IF p_f_end THEN                                                                                                                                                                                                    +
         -- Retrieve all assignments for the specified child entity                                                                                                                                                     +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.x_id_chd = p_x_id_chd;                                                                                                                                                                                   +
     ELSE                                                                                                                                                                                                               +
         -- Retrieve only active assignments (those without an end date)                                                                                                                                                +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.x_id_chd = p_x_id_chd                                                                                                                                                                                    +
             AND e.d_ent_asn_end IS NULL;                                                                                                                                                                               +
     END IF;                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list_by_child\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list_by_id(p_x_id_ent character varying, p_f_end boolean)                                                                                                          +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     IF p_f_end THEN                                                                                                                                                                                                    +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.x_id_pnt = p_x_id_ent OR e.x_id_chd = p_x_id_ent;                                                                                                                                                        +
     ELSE                                                                                                                                                                                                               +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             (e.x_id_pnt = p_x_id_ent OR e.x_id_chd = p_x_id_ent)                                                                                                                                                       +
             AND e.d_ent_asn_end IS NULL;                                                                                                                                                                               +
     END IF;                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list_by_key(p_i_asn_ent integer)                                                                                                                                   +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     RETURN QUERY                                                                                                                                                                                                       +
     SELECT                                                                                                                                                                                                             +
         e.i_asn_ent,                                                                                                                                                                                                   +
         e.x_id_pnt,                                                                                                                                                                                                    +
         e.x_id_chd,                                                                                                                                                                                                    +
         e.d_ent_asn_bgn,                                                                                                                                                                                               +
         e.d_ent_asn_end,                                                                                                                                                                                               +
         e.i_rsn,                                                                                                                                                                                                       +
         r.x_rsn                                                                                                                                                                                                        +
     FROM                                                                                                                                                                                                               +
         entityassmts e                                                                                                                                                                                                 +
     LEFT JOIN                                                                                                                                                                                                          +
         tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                         +
     WHERE                                                                                                                                                                                                              +
         e.i_asn_ent = p_i_asn_ent;                                                                                                                                                                                     +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list_by_key\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list_by_parent(p_x_id_pnt character varying, p_f_end boolean)                                                                                                      +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     IF p_f_end THEN                                                                                                                                                                                                    +
         -- Retrieve all assignments for the specified parent entity                                                                                                                                                    +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.x_id_pnt = p_x_id_pnt;                                                                                                                                                                                   +
     ELSE                                                                                                                                                                                                               +
         -- Retrieve only active assignments (those without an end date)                                                                                                                                                +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.x_id_pnt = p_x_id_pnt                                                                                                                                                                                    +
             AND e.d_ent_asn_end IS NULL;                                                                                                                                                                               +
     END IF;                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list_by_parent\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assign_entity_list_by_reason(p_i_rsn integer, p_f_end boolean)                                                                                                                   +
  RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)+
  LANGUAGE plpgsql                                                                                                                                                                                                      +
 AS $function$                                                                                                                                                                                                          +
 BEGIN                                                                                                                                                                                                                  +
     IF p_f_end THEN                                                                                                                                                                                                    +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.i_rsn = p_i_rsn;                                                                                                                                                                                         +
     ELSE                                                                                                                                                                                                               +
         RETURN QUERY                                                                                                                                                                                                   +
         SELECT                                                                                                                                                                                                         +
             e.i_asn_ent,                                                                                                                                                                                               +
             e.x_id_pnt,                                                                                                                                                                                                +
             e.x_id_chd,                                                                                                                                                                                                +
             e.d_ent_asn_bgn,                                                                                                                                                                                           +
             e.d_ent_asn_end,                                                                                                                                                                                           +
             e.i_rsn,                                                                                                                                                                                                   +
             r.x_rsn                                                                                                                                                                                                    +
         FROM                                                                                                                                                                                                           +
             entityassmts e                                                                                                                                                                                             +
         LEFT JOIN                                                                                                                                                                                                      +
             tlkassmtreasons r ON e.i_rsn = r.i_rsn                                                                                                                                                                     +
         WHERE                                                                                                                                                                                                          +
             e.i_rsn = p_i_rsn                                                                                                                                                                                          +
             AND e.d_ent_asn_end IS NULL;                                                                                                                                                                               +
     END IF;                                                                                                                                                                                                            +
 END;                                                                                                                                                                                                                   +
 $function$                                                                                                                                                                                                             +
 

Name: usp_assign_entity_list_by_reason\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assmt_reason_add(p_x_rsn character varying)+
  RETURNS integer                                                                 +
  LANGUAGE plpgsql                                                                +
 AS $function$                                                                    +
 DECLARE                                                                          +
     v_i_rsn INTEGER;                                                             +
 BEGIN                                                                            +
     INSERT INTO tlkassmtreasons (x_rsn)                                          +
     VALUES (p_x_rsn)                                                             +
     RETURNING i_rsn INTO v_i_rsn;                                                +
                                                                                  +
     RETURN v_i_rsn;  -- Return the new ID                                        +
 EXCEPTION                                                                        +
     WHEN OTHERS THEN                                                             +
         RAISE NOTICE 'Error: %', SQLERRM;                                        +
         RETURN -1;  -- Return -1 if an error occurs                              +
 END;                                                                             +
 $function$                                                                       +
 

Name: usp_assmt_reason_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assmt_reason_delete(p_i_rsn integer)+
  RETURNS integer                                                          +
  LANGUAGE plpgsql                                                         +
 AS $function$                                                             +
 BEGIN                                                                     +
     DELETE FROM tlkassmtreasons                                           +
     WHERE i_rsn = p_i_rsn;                                                +
                                                                           +
     IF FOUND THEN                                                         +
         RETURN 0;  -- Success                                             +
     ELSE                                                                  +
         RETURN 1;  -- No matching record found                            +
     END IF;                                                               +
                                                                           +
 EXCEPTION                                                                 +
     WHEN OTHERS THEN                                                      +
         RAISE NOTICE 'Error: %', SQLERRM;                                 +
         RETURN -1;  -- Error occurred                                     +
 END;                                                                      +
 $function$                                                                +
 

Name: usp_assmt_reason_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assmt_reason_edit(p_i_rsn integer, p_x_rsn character varying)+
  RETURNS integer                                                                                   +
  LANGUAGE plpgsql                                                                                  +
 AS $function$                                                                                      +
 BEGIN                                                                                              +
     UPDATE tlkassmtreasons                                                                         +
     SET x_rsn = p_x_rsn                                                                            +
     WHERE i_rsn = p_i_rsn;                                                                         +
                                                                                                    +
     IF FOUND THEN                                                                                  +
         RETURN 0;  -- Success                                                                      +
     ELSE                                                                                           +
         RETURN 1;  -- No matching record found                                                     +
     END IF;                                                                                        +
                                                                                                    +
 EXCEPTION                                                                                          +
     WHEN OTHERS THEN                                                                               +
         RAISE NOTICE 'Error: %', SQLERRM;                                                          +
         RETURN -1;  -- Error occurred                                                              +
 END;                                                                                               +
 $function$                                                                                         +
 

Name: usp_assmt_reason_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_assmt_reason_list()                    +
  RETURNS TABLE(i_rsn integer, x_rsn character varying)                       +
  LANGUAGE plpgsql                                                            +
 AS $function$                                                                +
 BEGIN                                                                        +
     RETURN QUERY                                                             +
     SELECT tlkassmtreasons.i_rsn, tlkassmtreasons.x_rsn FROM tlkassmtreasons;+
 END;                                                                         +
 $function$                                                                   +
 

Name: usp_assmt_reason_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_add(p_x_id_dev character varying, p_i_typ_dev integer, p_x_nm_dev character varying, p_d_srv_bgn timestamp without time zone, p_n_moe_x real DEFAULT NULL::real, p_n_moe_y real DEFAULT NULL::real, p_n_moe_z real DEFAULT NULL::real, p_zone_id integer DEFAULT NULL::integer)+
  RETURNS integer                                                                                                                                                                                                                                                                                                            +
  LANGUAGE plpgsql                                                                                                                                                                                                                                                                                                           +
 AS $function$                                                                                                                                                                                                                                                                                                               +
 DECLARE                                                                                                                                                                                                                                                                                                                     +
     result INTEGER;                                                                                                                                                                                                                                                                                                         +
 BEGIN                                                                                                                                                                                                                                                                                                                       +
     INSERT INTO devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, n_moe_x, n_moe_y, n_moe_z, f_log, zone_id)                                                                                                                                                                                                               +
     VALUES (p_x_id_dev, p_i_typ_dev, p_x_nm_dev, p_d_srv_bgn, p_n_moe_x, p_n_moe_y, p_n_moe_z, FALSE, p_zone_id)                                                                                                                                                                                                            +
     RETURNING 1 INTO result;                                                                                                                                                                                                                                                                                                +
                                                                                                                                                                                                                                                                                                                             +
     RETURN result;                                                                                                                                                                                                                                                                                                          +
 EXCEPTION                                                                                                                                                                                                                                                                                                                   +
     WHEN OTHERS THEN                                                                                                                                                                                                                                                                                                        +
         -- Log the error (optional, if you have a logging mechanism)                                                                                                                                                                                                                                                        +
         RAISE NOTICE 'Error in usp_device_add: %', SQLERRM;                                                                                                                                                                                                                                                                 +
         RETURN 0; -- Indicate failure                                                                                                                                                                                                                                                                                       +
 END;                                                                                                                                                                                                                                                                                                                        +
 $function$                                                                                                                                                                                                                                                                                                                  +
 

Name: usp_device_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_delete(p_x_id_dev character varying)+
  RETURNS integer                                                                 +
  LANGUAGE plpgsql                                                                +
 AS $function$                                                                    +
 BEGIN                                                                            +
     DELETE FROM public.devices WHERE x_id_dev = p_x_id_dev;                      +
     IF FOUND THEN                                                                +
         RETURN 1; -- Success: row deleted                                        +
     ELSE                                                                         +
         RETURN 0; -- No row found                                                +
     END IF;                                                                      +
 EXCEPTION WHEN OTHERS THEN                                                       +
     RETURN -1; -- Error                                                          +
 END;                                                                             +
 $function$                                                                       +
 

Name: usp_device_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_edit(p_x_id_dev character varying, p_new_x_id_dev character varying, p_i_typ_dev integer, p_x_nm_dev character varying, p_d_srv_bgn timestamp without time zone, p_d_srv_end timestamp without time zone, p_n_moe_x real, p_n_moe_y real, p_n_moe_z real, p_f_log boolean, p_zone_id integer)+
  RETURNS integer                                                                                                                                                                                                                                                                                                                          +
  LANGUAGE plpgsql                                                                                                                                                                                                                                                                                                                         +
 AS $function$                                                                                                                                                                                                                                                                                                                             +
 BEGIN                                                                                                                                                                                                                                                                                                                                     +
     UPDATE public.devices                                                                                                                                                                                                                                                                                                                 +
     SET x_id_dev = COALESCE(p_new_x_id_dev, x_id_dev),                                                                                                                                                                                                                                                                                    +
         i_typ_dev = COALESCE(p_i_typ_dev, i_typ_dev),                                                                                                                                                                                                                                                                                     +
         x_nm_dev = COALESCE(p_x_nm_dev, x_nm_dev),                                                                                                                                                                                                                                                                                        +
         d_srv_bgn = COALESCE(p_d_srv_bgn, d_srv_bgn),                                                                                                                                                                                                                                                                                     +
         d_srv_end = COALESCE(p_d_srv_end, d_srv_end),                                                                                                                                                                                                                                                                                     +
         n_moe_x = COALESCE(p_n_moe_x, n_moe_x),                                                                                                                                                                                                                                                                                           +
         n_moe_y = COALESCE(p_n_moe_y, n_moe_y),                                                                                                                                                                                                                                                                                           +
         n_moe_z = COALESCE(p_n_moe_z, n_moe_z),                                                                                                                                                                                                                                                                                           +
         f_log = COALESCE(p_f_log, f_log),                                                                                                                                                                                                                                                                                                 +
         zone_id = COALESCE(p_zone_id, zone_id)                                                                                                                                                                                                                                                                                            +
     WHERE x_id_dev = p_x_id_dev;                                                                                                                                                                                                                                                                                                          +
                                                                                                                                                                                                                                                                                                                                           +
     IF FOUND THEN                                                                                                                                                                                                                                                                                                                         +
         RETURN 1; -- Success                                                                                                                                                                                                                                                                                                              +
     ELSE                                                                                                                                                                                                                                                                                                                                  +
         RETURN 0; -- Device not found                                                                                                                                                                                                                                                                                                     +
     END IF;                                                                                                                                                                                                                                                                                                                               +
 EXCEPTION                                                                                                                                                                                                                                                                                                                                 +
     WHEN OTHERS THEN                                                                                                                                                                                                                                                                                                                      +
         RAISE NOTICE 'Error in usp_device_edit: %', SQLERRM;                                                                                                                                                                                                                                                                              +
         RETURN -1; -- Error                                                                                                                                                                                                                                                                                                               +
 END;                                                                                                                                                                                                                                                                                                                                      +
 $function$                                                                                                                                                                                                                                                                                                                                +
 

Name: usp_device_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_remove_end_date(p_x_id_dev character varying)+
  RETURNS integer                                                                          +
  LANGUAGE plpgsql                                                                         +
 AS $function$                                                                             +
 BEGIN                                                                                     +
     UPDATE devices                                                                        +
     SET d_srv_end = NULL                                                                  +
     WHERE x_id_dev = p_x_id_dev;                                                          +
                                                                                           +
     IF FOUND THEN                                                                         +
         RETURN 0;  -- Success                                                             +
     ELSE                                                                                  +
         RETURN 1;  -- No matching record found                                            +
     END IF;                                                                               +
                                                                                           +
 EXCEPTION                                                                                 +
     WHEN OTHERS THEN                                                                      +
         RAISE NOTICE 'Error: %', SQLERRM;                                                 +
         RETURN -1;  -- Error occurred                                                     +
 END;                                                                                      +
 $function$                                                                                +
 

Name: usp_device_remove_end_date\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_select_all()                                                                                                                                                                                        +
  RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean, zone_id integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                                                +
 AS $function$                                                                                                                                                                                                                                    +
 BEGIN                                                                                                                                                                                                                                            +
     RETURN QUERY SELECT d.x_id_dev, d.i_typ_dev, d.x_nm_dev, d.d_srv_bgn, d.d_srv_end, d.n_moe_x, d.n_moe_y, d.n_moe_z, d.f_log, d.zone_id                                                                                                       +
                  FROM devices d;                                                                                                                                                                                                                 +
 END;                                                                                                                                                                                                                                             +
 $function$                                                                                                                                                                                                                                       +
 

Name: usp_device_select_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_select_by_id(p_device_id character varying)                                                                                                                                                         +
  RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean, zone_id integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                                                +
 AS $function$                                                                                                                                                                                                                                    +
 BEGIN                                                                                                                                                                                                                                            +
     RETURN QUERY SELECT d.x_id_dev, d.i_typ_dev, d.x_nm_dev, d.d_srv_bgn, d.d_srv_end, d.n_moe_x, d.n_moe_y, d.n_moe_z, d.f_log, d.zone_id                                                                                                       +
                  FROM devices d                                                                                                                                                                                                                  +
                  WHERE d.x_id_dev = p_device_id;                                                                                                                                                                                                 +
 END;                                                                                                                                                                                                                                             +
 $function$                                                                                                                                                                                                                                       +
 

Name: usp_device_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_select_by_type(p_i_typ_dev integer)                                                                                                                                                +
  RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)+
  LANGUAGE plpgsql                                                                                                                                                                                                               +
 AS $function$                                                                                                                                                                                                                   +
 BEGIN                                                                                                                                                                                                                           +
     RETURN QUERY                                                                                                                                                                                                                +
     SELECT devices.x_id_dev, devices.i_typ_dev, devices.x_nm_dev,                                                                                                                                                               +
            devices.d_srv_bgn, devices.d_srv_end,                                                                                                                                                                                +
            devices.n_moe_x, devices.n_moe_y, devices.n_moe_z, devices.f_log                                                                                                                                                     +
     FROM devices                                                                                                                                                                                                                +
     WHERE devices.i_typ_dev = p_i_typ_dev;                                                                                                                                                                                      +
 END;                                                                                                                                                                                                                            +
 $function$                                                                                                                                                                                                                      +
 

Name: usp_device_select_by_type\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_select_outofservice()                                                                                                                                                              +
  RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)+
  LANGUAGE plpgsql                                                                                                                                                                                                               +
 AS $function$                                                                                                                                                                                                                   +
 BEGIN                                                                                                                                                                                                                           +
     RETURN QUERY                                                                                                                                                                                                                +
     SELECT devices.x_id_dev, devices.i_typ_dev, devices.x_nm_dev,                                                                                                                                                               +
            devices.d_srv_bgn, devices.d_srv_end,                                                                                                                                                                                +
            devices.n_moe_x, devices.n_moe_y, devices.n_moe_z, devices.f_log                                                                                                                                                     +
     FROM devices                                                                                                                                                                                                                +
     WHERE devices.d_srv_end IS NOT NULL;                                                                                                                                                                                        +
 END;                                                                                                                                                                                                                            +
 $function$                                                                                                                                                                                                                      +
 

Name: usp_device_select_outofservice\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_set_end_date(p_x_id_dev character varying, p_d_srv_end timestamp without time zone)+
  RETURNS integer                                                                                                                +
  LANGUAGE plpgsql                                                                                                               +
 AS $function$                                                                                                                   +
 BEGIN                                                                                                                           +
     UPDATE devices                                                                                                              +
     SET d_srv_end = p_d_srv_end                                                                                                 +
     WHERE x_id_dev = p_x_id_dev;                                                                                                +
                                                                                                                                 +
     IF FOUND THEN                                                                                                               +
         RETURN 0;  -- Success                                                                                                   +
     ELSE                                                                                                                        +
         RETURN 1;  -- No matching record found                                                                                  +
     END IF;                                                                                                                     +
                                                                                                                                 +
 EXCEPTION                                                                                                                       +
     WHEN OTHERS THEN                                                                                                            +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                                       +
         RETURN -1;  -- Error occurred                                                                                           +
 END;                                                                                                                            +
 $function$                                                                                                                      +
 

Name: usp_device_set_end_date\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_type_add(p_x_dsc_dev character varying)+
  RETURNS integer                                                                    +
  LANGUAGE plpgsql                                                                   +
 AS $function$                                                                       +
 DECLARE                                                                             +
     v_i_typ_dev INTEGER;                                                            +
 BEGIN                                                                               +
     INSERT INTO public.tlkdevicetypes (x_dsc_dev)                                   +
     VALUES (p_x_dsc_dev)                                                            +
     RETURNING i_typ_dev INTO v_i_typ_dev;                                           +
                                                                                     +
     RETURN v_i_typ_dev; -- Return the new device type ID                            +
 EXCEPTION                                                                           +
     WHEN unique_violation THEN                                                      +
         RAISE NOTICE 'Device type description % already exists', p_x_dsc_dev;       +
         RETURN -2; -- Duplicate description                                         +
     WHEN OTHERS THEN                                                                +
         RAISE NOTICE 'Error in usp_device_type_add: %', SQLERRM;                    +
         RETURN -1; -- Other error                                                   +
 END;                                                                                +
 $function$                                                                          +
 

Name: usp_device_type_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_type_delete(p_i_typ_dev integer)+
  RETURNS integer                                                             +
  LANGUAGE plpgsql                                                            +
 AS $function$                                                                +
 BEGIN                                                                        +
     DELETE FROM tlkdevicetypes                                               +
     WHERE i_typ_dev = p_i_typ_dev;                                           +
                                                                              +
     IF FOUND THEN                                                            +
         RETURN 0;  -- Success                                                +
     ELSE                                                                     +
         RETURN 1;  -- No matching record found                               +
     END IF;                                                                  +
                                                                              +
 EXCEPTION                                                                    +
     WHEN OTHERS THEN                                                         +
         RAISE NOTICE 'Error: %', SQLERRM;                                    +
         RETURN -1;  -- Error occurred                                        +
 END;                                                                         +
 $function$                                                                   +
 

Name: usp_device_type_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_type_edit(p_i_typ_dev integer, p_x_dsc_dev character varying)+
  RETURNS integer                                                                                          +
  LANGUAGE plpgsql                                                                                         +
 AS $function$                                                                                             +
 BEGIN                                                                                                     +
     UPDATE tlkdevicetypes                                                                                 +
     SET x_dsc_dev = p_x_dsc_dev                                                                           +
     WHERE i_typ_dev = p_i_typ_dev;                                                                        +
                                                                                                           +
     IF FOUND THEN                                                                                         +
         RETURN 0;  -- Success                                                                             +
     ELSE                                                                                                  +
         RETURN 1;  -- No matching record found                                                            +
     END IF;                                                                                               +
                                                                                                           +
 EXCEPTION                                                                                                 +
     WHEN OTHERS THEN                                                                                      +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                 +
         RETURN -1;  -- Error occurred                                                                     +
 END;                                                                                                      +
 $function$                                                                                                +
 

Name: usp_device_type_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_device_type_list()      +
  RETURNS TABLE(i_typ_dev integer, x_dsc_dev character varying)+
  LANGUAGE plpgsql                                             +
 AS $function$                                                 +
 BEGIN                                                         +
     RETURN QUERY                                              +
     SELECT tlkdevicetypes.i_typ_dev, tlkdevicetypes.x_dsc_dev +
     FROM tlkdevicetypes;                                      +
 END;                                                          +
 $function$                                                    +
 

Name: usp_device_type_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_add(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone)+
  RETURNS integer                                                                                                                                                                                           +
  LANGUAGE plpgsql                                                                                                                                                                                          +
 AS $function$                                                                                                                                                                                              +
 DECLARE                                                                                                                                                                                                    +
     new_entity_id INTEGER;                                                                                                                                                                                 +
 BEGIN                                                                                                                                                                                                      +
     -- Insert the entity and return the new ID                                                                                                                                                             +
     INSERT INTO public.entities (X_ID_ENT, I_TYP_ENT, X_NM_ENT, D_CRT, D_UDT)                                                                                                                              +
     VALUES (p_x_id_ent, p_i_typ_ent, p_x_nm_ent, p_d_crt, p_d_udt)                                                                                                                                         +
     RETURNING I_TYP_ENT INTO new_entity_id;                                                                                                                                                                +
                                                                                                                                                                                                            +
     -- Return the newly created entity ID                                                                                                                                                                  +
     RETURN new_entity_id;                                                                                                                                                                                  +
 END;                                                                                                                                                                                                       +
 $function$                                                                                                                                                                                                 +
 

Name: usp_entity_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_all()                                                                                                             +
  RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         e.X_ID_ENT,                                                                                                                                            +
         e.I_TYP_ENT,                                                                                                                                           +
         e.X_NM_ENT,                                                                                                                                            +
         e.D_CRT,                                                                                                                                               +
         e.D_UDT                                                                                                                                                +
     FROM Entities e;                                                                                                                                           +
                                                                                                                                                                +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_entity_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_by_id(p_x_id_ent character varying)                                                                               +
  RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         e.X_ID_ENT,                                                                                                                                            +
         e.I_TYP_ENT,                                                                                                                                           +
         e.X_NM_ENT,                                                                                                                                            +
         e.D_CRT,                                                                                                                                               +
         e.D_UDT                                                                                                                                                +
     FROM Entities e                                                                                                                                            +
     WHERE e.X_ID_ENT = p_x_id_ent;                                                                                                                             +
                                                                                                                                                                +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_entity_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_by_type(p_i_typ_ent integer)                                                                                      +
  RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         e.X_ID_ENT,                                                                                                                                            +
         e.I_TYP_ENT,                                                                                                                                           +
         e.X_NM_ENT,                                                                                                                                            +
         e.D_CRT,                                                                                                                                               +
         e.D_UDT                                                                                                                                                +
     FROM Entities e                                                                                                                                            +
     WHERE e.I_TYP_ENT = p_i_typ_ent;                                                                                                                           +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_entity_by_type\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_delete(p_x_id_ent character varying)+
  RETURNS integer                                                                 +
  LANGUAGE plpgsql                                                                +
 AS $function$                                                                    +
 DECLARE                                                                          +
     delete_error INTEGER := 0;                                                   +
 BEGIN                                                                            +
     -- Delete the entity                                                         +
     DELETE FROM public.entities WHERE X_ID_ENT = p_x_id_ent;                     +
                                                                                  +
     -- Capture error code (0 means success, 1 means failure)                     +
     GET DIAGNOSTICS delete_error = ROW_COUNT;                                    +
                                                                                  +
     -- If no rows were deleted, return 1 (similar to @@ERROR in MSSQL)           +
     IF delete_error = 0 THEN                                                     +
         RETURN 1;                                                                +
     END IF;                                                                      +
                                                                                  +
     -- Otherwise, return success                                                 +
     RETURN 0;                                                                    +
                                                                                  +
 END;                                                                             +
 $function$                                                                       +
 

Name: usp_entity_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_edit(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying)+
  RETURNS integer                                                                                                                  +
  LANGUAGE plpgsql                                                                                                                 +
 AS $function$                                                                                                                     +
 DECLARE                                                                                                                           +
     v_d_udt TIMESTAMP WITHOUT TIME ZONE := NOW();                                                                                 +
     entity_exists INT;                                                                                                            +
 BEGIN                                                                                                                             +
     -- Check if the entity exists                                                                                                 +
     SELECT COUNT(*) INTO entity_exists FROM public.entities WHERE X_ID_ENT = p_x_id_ent;                                          +
                                                                                                                                   +
     IF entity_exists = 0 THEN                                                                                                     +
         RAISE EXCEPTION 'Entity ID % not found.', p_x_id_ent;                                                                     +
     END IF;                                                                                                                       +
                                                                                                                                   +
     -- Update the entity                                                                                                          +
     UPDATE public.entities                                                                                                        +
     SET                                                                                                                           +
         I_TYP_ENT = p_i_typ_ent,                                                                                                  +
         X_NM_ENT = p_x_nm_ent,                                                                                                    +
         D_UDT = v_d_udt                                                                                                           +
     WHERE X_ID_ENT = p_x_id_ent;                                                                                                  +
                                                                                                                                   +
     -- Return 0 for success                                                                                                       +
     RETURN 0;                                                                                                                     +
 END;                                                                                                                              +
 $function$                                                                                                                        +
 

Name: usp_entity_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone)+
  RETURNS text                                                                                                                                                                              +
  LANGUAGE plpgsql                                                                                                                                                                          +
 AS $function$                                                                                                                                                                              +
 BEGIN                                                                                                                                                                                      +
     INSERT INTO EntityTypes (X_ID_TYP, X_NM_TYP, D_CRT, D_UDT)                                                                                                                             +
     VALUES (p_x_id_typ, p_x_nm_typ, p_d_crt, p_d_udt);                                                                                                                                     +
                                                                                                                                                                                            +
     RETURN 'Entity type added successfully';                                                                                                                                               +
 EXCEPTION WHEN OTHERS THEN                                                                                                                                                                 +
     RETURN 'Error: ' || SQLERRM;                                                                                                                                                           +
 END;                                                                                                                                                                                       +
 $function$                                                                                                                                                                                 +
 

Name: usp_entity_type_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_add(p_x_nm_typ character varying)+
  RETURNS integer                                                                   +
  LANGUAGE plpgsql                                                                  +
 AS $function$                                                                      +
 DECLARE                                                                            +
     v_i_typ_ent INTEGER;                                                           +
 BEGIN                                                                              +
     INSERT INTO entitytypes (x_nm_typ)                                             +
     VALUES (p_x_nm_typ)                                                            +
     RETURNING x_id_typ INTO v_i_typ_ent;                                           +
                                                                                    +
     RETURN v_i_typ_ent;  -- Return the new ID                                      +
 EXCEPTION                                                                          +
     WHEN OTHERS THEN                                                               +
         RAISE NOTICE 'Error: %', SQLERRM;                                          +
         RETURN -1;  -- Return -1 if an error occurs                                +
 END;                                                                               +
 $function$                                                                         +
 

Name: usp_entity_type_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying)+
  RETURNS character varying                                                                                       +
  LANGUAGE plpgsql                                                                                                +
 AS $function$                                                                                                    +
 BEGIN                                                                                                            +
     INSERT INTO entitytypes (x_id_typ, x_nm_typ, d_crt)                                                          +
     VALUES (p_x_id_typ, p_x_nm_typ, NOW());                                                                      +
                                                                                                                  +
     RETURN p_x_id_typ;  -- Return the new key                                                                    +
 EXCEPTION                                                                                                        +
     WHEN OTHERS THEN                                                                                             +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                        +
         RETURN NULL;  -- Return NULL if an error occurs                                                          +
 END;                                                                                                             +
 $function$                                                                                                       +
 

Name: usp_entity_type_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_delete(p_x_id_typ character varying)+
  RETURNS integer                                                                      +
  LANGUAGE plpgsql                                                                     +
 AS $function$                                                                         +
 BEGIN                                                                                 +
     DELETE FROM entitytypes                                                           +
     WHERE x_id_typ = p_x_id_typ;                                                      +
                                                                                       +
     IF FOUND THEN                                                                     +
         RETURN 0;  -- Success                                                         +
     ELSE                                                                              +
         RETURN 1;  -- No matching record found                                        +
     END IF;                                                                           +
                                                                                       +
 EXCEPTION                                                                             +
     WHEN OTHERS THEN                                                                  +
         RAISE NOTICE 'Error: %', SQLERRM;                                             +
         RETURN -1;  -- Error occurred                                                 +
 END;                                                                                  +
 $function$                                                                            +
 

Name: usp_entity_type_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_edit(p_x_id_typ character varying, p_x_nm_typ character varying)+
  RETURNS integer                                                                                                  +
  LANGUAGE plpgsql                                                                                                 +
 AS $function$                                                                                                     +
 BEGIN                                                                                                             +
     UPDATE entitytypes                                                                                            +
     SET x_nm_typ = p_x_nm_typ,                                                                                    +
         d_udt = NOW()  -- Update timestamp                                                                        +
     WHERE x_id_typ = p_x_id_typ;                                                                                  +
                                                                                                                   +
     IF FOUND THEN                                                                                                 +
         RETURN 0;  -- Success                                                                                     +
     ELSE                                                                                                          +
         RETURN 1;  -- No matching record found                                                                    +
     END IF;                                                                                                       +
                                                                                                                   +
 EXCEPTION                                                                                                         +
     WHEN OTHERS THEN                                                                                              +
         RAISE NOTICE 'Error: %', SQLERRM;                                                                         +
         RETURN -1;  -- Error occurred                                                                             +
 END;                                                                                                              +
 $function$                                                                                                        +
 

Name: usp_entity_type_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_entity_type_list()                                                                                      +
  RETURNS TABLE(i_typ_ent character varying, x_dsc_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)+
  LANGUAGE plpgsql                                                                                                                             +
 AS $function$                                                                                                                                 +
 BEGIN                                                                                                                                         +
     RETURN QUERY                                                                                                                              +
     SELECT                                                                                                                                    +
         t.i_typ_ent,                                                                                                                          +
         t.x_dsc_ent,                                                                                                                          +
         t.d_crt,                                                                                                                              +
         t.d_udt                                                                                                                               +
     FROM public.tlkentitytypes t; -- ✅ Explicit alias to prevent ambiguity                                                                   +
 END;                                                                                                                                          +
 $function$                                                                                                                                    +
 

Name: usp_entity_type_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_getallzonesforcampus(in_campus_id integer)        +
  RETURNS jsonb                                                                          +
  LANGUAGE plpgsql                                                                       +
 AS $function$                                                                           +
 DECLARE                                                                                 +
     campus_exists BOOLEAN;                                                              +
 BEGIN                                                                                   +
     -- Check if the input campus_id exists and is a Campus L1 zone                      +
     SELECT EXISTS(SELECT 1 FROM zones WHERE i_zn = in_campus_id AND i_typ_zn = 1)       +
     INTO campus_exists;                                                                 +
                                                                                         +
     IF NOT campus_exists THEN                                                           +
         RAISE NOTICE 'Invalid campus_id: %', in_campus_id;                              +
         RETURN jsonb_build_object('error', 'Invalid Campus ID or not a Campus L1 zone');+
     END IF;                                                                             +
                                                                                         +
     -- Recursive query to retrieve all child zones                                      +
     RETURN (                                                                            +
         WITH RECURSIVE zone_hierarchy AS (                                              +
             -- Base Case: Start with the specified Campus L1 zone                       +
             SELECT                                                                      +
                 z.i_zn,                                                                 +
                 z.x_nm_zn AS name,                                                      +
                 z.i_typ_zn AS zone_type,                                                +
                 z.i_pnt_zn AS parent_zone_id,                                           +
                 z.i_map AS map_id                                                       +
             FROM zones z                                                                +
             WHERE z.i_zn = in_campus_id                                                 +
             AND z.i_typ_zn = 1                                                          +
                                                                                         +
             UNION ALL                                                                   +
                                                                                         +
             -- Recursive Case: Fetch child zones based on parent relationships          +
             SELECT                                                                      +
                 z.i_zn,                                                                 +
                 z.x_nm_zn AS name,                                                      +
                 z.i_typ_zn AS zone_type,                                                +
                 z.i_pnt_zn AS parent_zone_id,                                           +
                 z.i_map AS map_id                                                       +
             FROM zones z                                                                +
             JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn                              +
             WHERE z.i_typ_zn IN (1, 2, 3, 4, 5, 10)  -- Include all zone types          +
               AND z.i_pnt_zn IS NOT NULL                                                +
               AND z.i_zn IS NOT NULL                                                    +
               AND z.i_pnt_zn != 0                                                       +
         )                                                                               +
                                                                                         +
         -- Construct JSON output with full recursive children                           +
         SELECT jsonb_build_object(                                                      +
             'zones',                                                                    +
             jsonb_agg(                                                                  +
                 jsonb_build_object(                                                     +
                     'zone_id', zh.i_zn,                                                 +
                     'name', COALESCE(zh.name, 'Unnamed'),                               +
                     'zone_type', zh.zone_type,                                          +
                     'parent_zone_id', zh.parent_zone_id,                                +
                     'map_id', zh.map_id,                                                +
                     'children', (                                                       +
                         -- Fetch children recursively using a separate WITH clause      +
                         WITH RECURSIVE recursive_children AS (                          +
                             SELECT                                                      +
                                 child.i_zn,                                             +
                                 child.x_nm_zn AS name,                                  +
                                 child.i_typ_zn AS zone_type,                            +
                                 child.i_pnt_zn AS parent_zone_id,                       +
                                 child.i_map AS map_id                                   +
                             FROM zones child                                            +
                             WHERE child.i_pnt_zn = zh.i_zn                              +
                                                                                         +
                             UNION ALL                                                   +
                                                                                         +
                             SELECT                                                      +
                                 grandchild.i_zn,                                        +
                                 grandchild.x_nm_zn AS name,                             +
                                 grandchild.i_typ_zn AS zone_type,                       +
                                 grandchild.i_pnt_zn AS parent_zone_id,                  +
                                 grandchild.i_map AS map_id                              +
                             FROM zones grandchild                                       +
                             JOIN recursive_children rc ON grandchild.i_pnt_zn = rc.i_zn +
                         )                                                               +
                         SELECT COALESCE(jsonb_agg(                                      +
                             jsonb_build_object(                                         +
                                 'zone_id', i_zn,                                        +
                                 'name', COALESCE(name, 'Unnamed'),                      +
                                 'zone_type', zone_type,                                 +
                                 'parent_zone_id', parent_zone_id,                       +
                                 'map_id', map_id                                        +
                             )                                                           +
                         ), '[]'::jsonb)                                                 +
                         FROM recursive_children                                         +
                     )                                                                   +
                 )                                                                       +
             )                                                                           +
         )                                                                               +
         FROM zone_hierarchy zh                                                          +
         WHERE zh.i_zn = in_campus_id                                                    +
     );                                                                                  +
 END;                                                                                    +
 $function$                                                                              +
 

Name: usp_getallzonesforcampus\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_history_insert(entity_id integer, location_x real, location_y real, location_z real, timestamp_utc timestamp without time zone)+
  RETURNS void                                                                                                                                                        +
  LANGUAGE plpgsql                                                                                                                                                    +
 AS $function$                                                                                                                                                        +
 DECLARE                                                                                                                                                              +
     entity_exists INT;                                                                                                                                               +
 BEGIN                                                                                                                                                                +
     -- Check if the entity exists                                                                                                                                    +
     SELECT COUNT(*) INTO entity_exists FROM public.entities WHERE i_ent = entity_id;                                                                                 +
                                                                                                                                                                      +
     IF entity_exists = 0 THEN                                                                                                                                        +
         RAISE EXCEPTION 'Entity ID % not found.', entity_id;                                                                                                         +
     END IF;                                                                                                                                                          +
                                                                                                                                                                      +
     -- Insert the new history record                                                                                                                                 +
     INSERT INTO public.history (i_ent, n_x, n_y, n_z, d_timestamp)                                                                                                   +
     VALUES (entity_id, location_x, location_y, location_z, timestamp_utc);                                                                                           +
 END;                                                                                                                                                                 +
 $function$                                                                                                                                                           +
 

Name: usp_history_insert\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_map_delete(map_id integer)          +
  RETURNS void                                                             +
  LANGUAGE plpgsql                                                         +
 AS $function$                                                             +
 DECLARE                                                                   +
     map_exists INT;                                                       +
 BEGIN                                                                     +
     -- Check if the map exists                                            +
     SELECT COUNT(*) INTO map_exists FROM public.maps WHERE i_map = map_id;+
                                                                           +
     IF map_exists = 0 THEN                                                +
         RAISE EXCEPTION 'Map ID % not found.', map_id;                    +
     END IF;                                                               +
                                                                           +
     -- Perform the delete operation                                       +
     DELETE FROM public.maps WHERE i_map = map_id;                         +
 END;                                                                      +
 $function$                                                                +
 

Name: usp_map_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_map_insert(map_name character varying, map_path character varying, map_format character varying, map_scale real, zone_id integer)+
  RETURNS void                                                                                                                                                          +
  LANGUAGE plpgsql                                                                                                                                                      +
 AS $function$                                                                                                                                                          +
 DECLARE                                                                                                                                                                +
     zone_exists INT;                                                                                                                                                   +
 BEGIN                                                                                                                                                                  +
     -- Check if the zone exists                                                                                                                                        +
     SELECT COUNT(*) INTO zone_exists FROM public.zones WHERE i_zn = zone_id;                                                                                           +
                                                                                                                                                                        +
     IF zone_exists = 0 THEN                                                                                                                                            +
         RAISE EXCEPTION 'Zone ID % not found.', zone_id;                                                                                                               +
     END IF;                                                                                                                                                            +
                                                                                                                                                                        +
     -- Validate format                                                                                                                                                 +
     IF map_format NOT IN ('GIF', 'PNG', 'JPG', 'JPEG', 'BMP') THEN                                                                                                     +
         RAISE EXCEPTION 'Invalid map format. Allowed: GIF, PNG, JPG, JPEG, BMP.';                                                                                      +
     END IF;                                                                                                                                                            +
                                                                                                                                                                        +
     -- Insert the new map                                                                                                                                              +
     INSERT INTO public.maps (x_nm_map, x_path, x_format, n_scale, i_zn, d_uploaded)                                                                                    +
     VALUES (map_name, map_path, map_format, map_scale, zone_id, NOW());                                                                                                +
 END;                                                                                                                                                                   +
 $function$                                                                                                                                                             +
 

Name: usp_map_insert\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_map_list()                                                               +
  RETURNS TABLE(i_map integer, x_nm_map character varying, x_path character varying, n_scale real, i_zn integer)+
  LANGUAGE plpgsql                                                                                              +
 AS $function$                                                                                                  +
 BEGIN                                                                                                          +
     RETURN QUERY                                                                                               +
     SELECT                                                                                                     +
         m.i_map,                                                                                               +
         m.x_nm_map,                                                                                            +
         m.x_path,                                                                                              +
         m.n_scale,                                                                                             +
         m.i_zn                                                                                                 +
     FROM public.maps m;                                                                                        +
 END;                                                                                                           +
 $function$                                                                                                     +
 

Name: usp_map_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_portable_trigger_add(p_tag_id text, p_name text, p_direction_id integer, p_radius double precision, p_zmin double precision, p_zmax double precision)+
  RETURNS integer                                                                                                                                                                           +
  LANGUAGE plpgsql                                                                                                                                                                          +
 AS $function$                                                                                                                                                                              +
 DECLARE                                                                                                                                                                                    +
     trig_id INT;                                                                                                                                                                           +
 BEGIN                                                                                                                                                                                      +
     INSERT INTO triggers (                                                                                                                                                                 +
         x_nm_trg, i_dir, f_ign, ignore_unknowns,                                                                                                                                           +
         is_portable, assigned_tag_id, radius_ft, z_min, z_max                                                                                                                              +
     )                                                                                                                                                                                      +
     VALUES (                                                                                                                                                                               +
         p_name, p_direction_id, FALSE, FALSE,                                                                                                                                              +
         TRUE, p_tag_id, p_radius, p_zmin, p_zmax                                                                                                                                           +
     )                                                                                                                                                                                      +
     RETURNING i_trg INTO trig_id;                                                                                                                                                          +
     RETURN trig_id;                                                                                                                                                                        +
 END;                                                                                                                                                                                       +
 $function$                                                                                                                                                                                 +
 

Name: usp_portable_trigger_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_region_add(p_i_rgn integer, p_i_zn integer, p_x_nm_rgn character varying, p_n_max_x real, p_n_max_y real, p_n_max_z real, p_n_min_x real, p_n_min_y real, p_n_min_z real, p_i_trg integer)+
  RETURNS integer                                                                                                                                                                                                                +
  LANGUAGE plpgsql                                                                                                                                                                                                               +
 AS $function$                                                                                                                                                                                                                   +
 DECLARE                                                                                                                                                                                                                         +
     v_i_rgn integer;                                                                                                                                                                                                            +
 BEGIN                                                                                                                                                                                                                           +
     -- Insert into regions table                                                                                                                                                                                                +
     INSERT INTO public.regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z, i_trg)                                                                                                                    +
     VALUES (p_i_zn, p_x_nm_rgn, p_n_max_x, p_n_max_y, p_n_max_z, p_n_min_x, p_n_min_y, p_n_min_z, p_i_trg)                                                                                                                      +
     RETURNING i_rgn INTO v_i_rgn;                                                                                                                                                                                               +
     RETURN v_i_rgn;                                                                                                                                                                                                             +
 EXCEPTION                                                                                                                                                                                                                       +
     WHEN OTHERS THEN                                                                                                                                                                                                            +
         RAISE NOTICE 'Error in usp_region_add: %', SQLERRM;                                                                                                                                                                     +
         RETURN -1;  -- Error indicator                                                                                                                                                                                          +
 END;                                                                                                                                                                                                                            +
 $function$                                                                                                                                                                                                                      +
 

Name: usp_region_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_region_delete(region_id integer)             +
  RETURNS void                                                                      +
  LANGUAGE plpgsql                                                                  +
 AS $function$                                                                      +
 DECLARE                                                                            +
     region_exists INT;                                                             +
 BEGIN                                                                              +
     -- Check if the region exists                                                  +
     SELECT COUNT(*) INTO region_exists FROM public.regions WHERE i_rgn = region_id;+
                                                                                    +
     IF region_exists = 0 THEN                                                      +
         RAISE EXCEPTION 'Region ID % not found.', region_id;                       +
     END IF;                                                                        +
                                                                                    +
     -- Perform the delete operation                                                +
     DELETE FROM public.regions WHERE i_rgn = region_id;                            +
 END;                                                                               +
 $function$                                                                         +
 

Name: usp_region_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_region_edit(region_id integer, zone_id integer, region_name character varying, max_x integer, max_y integer, max_z integer, min_x integer, min_y integer, min_z integer, trigger_id integer)+
  RETURNS void                                                                                                                                                                                                                     +
  LANGUAGE plpgsql                                                                                                                                                                                                                 +
 AS $function$                                                                                                                                                                                                                     +
 DECLARE                                                                                                                                                                                                                           +
     region_exists INT;                                                                                                                                                                                                            +
 BEGIN                                                                                                                                                                                                                             +
     -- Check if the region exists                                                                                                                                                                                                 +
     SELECT COUNT(*) INTO region_exists FROM public.regions WHERE i_rgn = region_id;                                                                                                                                               +
                                                                                                                                                                                                                                   +
     IF region_exists = 0 THEN                                                                                                                                                                                                     +
         RAISE EXCEPTION 'Region ID % not found.', region_id;                                                                                                                                                                      +
     END IF;                                                                                                                                                                                                                       +
                                                                                                                                                                                                                                   +
     -- Update the region                                                                                                                                                                                                          +
     UPDATE public.regions                                                                                                                                                                                                         +
     SET                                                                                                                                                                                                                           +
         i_zn = zone_id,                                                                                                                                                                                                           +
         x_nm_rgn = region_name,                                                                                                                                                                                                   +
         n_max_x = max_x,                                                                                                                                                                                                          +
         n_max_y = max_y,                                                                                                                                                                                                          +
         n_max_z = max_z,                                                                                                                                                                                                          +
         n_min_x = min_x,                                                                                                                                                                                                          +
         n_min_y = min_y,                                                                                                                                                                                                          +
         n_min_z = min_z,                                                                                                                                                                                                          +
         i_trg = trigger_id                                                                                                                                                                                                        +
     WHERE i_rgn = region_id;                                                                                                                                                                                                      +
 END;                                                                                                                                                                                                                              +
 $function$                                                                                                                                                                                                                        +
 

Name: usp_region_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_region_list()                                                                                                                       +
  RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x real, n_max_y real, n_max_z real, n_min_x real, n_min_y real, n_min_z real, i_trg integer)+
  LANGUAGE plpgsql                                                                                                                                                         +
 AS $function$                                                                                                                                                             +
 BEGIN                                                                                                                                                                     +
     RETURN QUERY                                                                                                                                                          +
     SELECT                                                                                                                                                                +
         r.i_rgn,                                                                                                                                                          +
         r.i_zn,                                                                                                                                                           +
         r.x_nm_rgn,                                                                                                                                                       +
         r.n_max_x,                                                                                                                                                        +
         r.n_max_y,                                                                                                                                                        +
         r.n_max_z,                                                                                                                                                        +
         r.n_min_x,                                                                                                                                                        +
         r.n_min_y,                                                                                                                                                        +
         r.n_min_z,                                                                                                                                                        +
         r.i_trg                                                                                                                                                           +
     FROM public.regions r;                                                                                                                                                +
 END;                                                                                                                                                                      +
 $function$                                                                                                                                                                +
 

Name: usp_region_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_region_select_by_id(region_id integer)                                                                                              +
  RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x real, n_max_y real, n_max_z real, n_min_x real, n_min_y real, n_min_z real, i_trg integer)+
  LANGUAGE plpgsql                                                                                                                                                         +
 AS $function$                                                                                                                                                             +
 BEGIN                                                                                                                                                                     +
     RETURN QUERY                                                                                                                                                          +
     SELECT                                                                                                                                                                +
         r.i_rgn,                                                                                                                                                          +
         r.i_zn,                                                                                                                                                           +
         r.x_nm_rgn,                                                                                                                                                       +
         r.n_max_x,                                                                                                                                                        +
         r.n_max_y,                                                                                                                                                        +
         r.n_max_z,                                                                                                                                                        +
         r.n_min_x,                                                                                                                                                        +
         r.n_min_y,                                                                                                                                                        +
         r.n_min_z,                                                                                                                                                        +
         r.i_trg                                                                                                                                                           +
     FROM public.regions r                                                                                                                                                 +
     WHERE r.i_rgn = region_id;                                                                                                                                            +
 END;                                                                                                                                                                      +
 $function$                                                                                                                                                                +
 

Name: usp_region_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_regions_select()                                                                                                                                      +
  RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer)+
  LANGUAGE plpgsql                                                                                                                                                                           +
 AS $function$                                                                                                                                                                               +
 BEGIN                                                                                                                                                                                       +
     RETURN QUERY                                                                                                                                                                            +
     SELECT                                                                                                                                                                                  +
         r.i_rgn,                                                                                                                                                                            +
         r.i_zn,                                                                                                                                                                             +
         r.x_nm_rgn,                                                                                                                                                                         +
         r.n_max_x::NUMERIC(18,2),                                                                                                                                                           +
         r.n_max_y::NUMERIC(18,2),                                                                                                                                                           +
         r.n_max_z::NUMERIC(18,2),                                                                                                                                                           +
         r.n_min_x::NUMERIC(18,2),                                                                                                                                                           +
         r.n_min_y::NUMERIC(18,2),                                                                                                                                                           +
         r.n_min_z::NUMERIC(18,2),                                                                                                                                                           +
         r.i_trg                                                                                                                                                                             +
     FROM public.regions r;  -- ✅ Explicit table alias                                                                                                                                      +
 END;                                                                                                                                                                                        +
 $function$                                                                                                                                                                                  +
 

Name: usp_regions_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_regions_select_by_trigger(trigger_id integer)                                                                                                                                                                              +
  RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                                                                +
 AS $function$                                                                                                                                                                                                                                                    +
 BEGIN                                                                                                                                                                                                                                                            +
     RETURN QUERY                                                                                                                                                                                                                                                 +
     SELECT                                                                                                                                                                                                                                                       +
         r.i_rgn,                                                                                                                                                                                                                                                 +
         r.i_zn,                                                                                                                                                                                                                                                  +
         r.x_nm_rgn,                                                                                                                                                                                                                                              +
         r.n_max_x::NUMERIC(18,2),  -- Explicit cast                                                                                                                                                                                                              +
         r.n_max_y::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_max_z::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_x::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_y::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_z::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.i_trg,                                                                                                                                                                                                                                                 +
         v.n_x::NUMERIC(18,2),  -- Explicit cast                                                                                                                                                                                                                  +
         v.n_y::NUMERIC(18,2),                                                                                                                                                                                                                                    +
         v.n_z::NUMERIC(18,2),                                                                                                                                                                                                                                    +
         v.n_ord,                                                                                                                                                                                                                                                 +
         v.i_vtx                                                                                                                                                                                                                                                  +
     FROM public.regions r                                                                                                                                                                                                                                        +
     LEFT OUTER JOIN public.vertices v                                                                                                                                                                                                                            +
     ON r.i_rgn = v.i_rgn                                                                                                                                                                                                                                         +
     WHERE r.i_trg = trigger_id;                                                                                                                                                                                                                                  +
 END;                                                                                                                                                                                                                                                             +
 $function$                                                                                                                                                                                                                                                       +
 

Name: usp_regions_select_by_trigger\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_regions_select_by_zone(zone_id integer)                                                                                                                                                                                    +
  RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                                                                +
 AS $function$                                                                                                                                                                                                                                                    +
 BEGIN                                                                                                                                                                                                                                                            +
     RETURN QUERY                                                                                                                                                                                                                                                 +
     SELECT                                                                                                                                                                                                                                                       +
         r.i_rgn,                                                                                                                                                                                                                                                 +
         r.i_zn,                                                                                                                                                                                                                                                  +
         r.x_nm_rgn,                                                                                                                                                                                                                                              +
         r.n_max_x::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_max_y::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_max_z::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_x::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_y::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.n_min_z::NUMERIC(18,2),                                                                                                                                                                                                                                +
         r.i_trg,                                                                                                                                                                                                                                                 +
         v.n_x::NUMERIC(18,2),                                                                                                                                                                                                                                    +
         v.n_y::NUMERIC(18,2),                                                                                                                                                                                                                                    +
         v.n_z::NUMERIC(18,2),                                                                                                                                                                                                                                    +
         v.n_ord,                                                                                                                                                                                                                                                 +
         v.i_vtx                                                                                                                                                                                                                                                  +
     FROM public.regions r                                                                                                                                                                                                                                        +
     LEFT OUTER JOIN public.vertices v                                                                                                                                                                                                                            +
     ON r.i_rgn = v.i_rgn                                                                                                                                                                                                                                         +
     WHERE r.i_zn = zone_id;                                                                                                                                                                                                                                      +
 END;                                                                                                                                                                                                                                                             +
 $function$                                                                                                                                                                                                                                                       +
 

Name: usp_regions_select_by_zone\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resource_delete(resource_id integer)                  +
  RETURNS void                                                                               +
  LANGUAGE plpgsql                                                                           +
 AS $function$                                                                               +
 DECLARE                                                                                     +
     resource_exists INT;                                                                    +
 BEGIN                                                                                       +
     -- Check if the resource exists                                                         +
     SELECT COUNT(*) INTO resource_exists FROM public.tlkresources WHERE i_res = resource_id;+
                                                                                             +
     IF resource_exists = 0 THEN                                                             +
         RAISE EXCEPTION 'Resource ID % not found.', resource_id;                            +
     END IF;                                                                                 +
                                                                                             +
     -- Perform the delete operation                                                         +
     DELETE FROM public.tlkresources WHERE i_res = resource_id;                              +
 END;                                                                                        +
 $function$                                                                                  +
 

Name: usp_resource_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resource_edit(resource_id integer, resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean)+
  RETURNS void                                                                                                                                                                                                                                           +
  LANGUAGE plpgsql                                                                                                                                                                                                                                       +
 AS $function$                                                                                                                                                                                                                                           +
 DECLARE                                                                                                                                                                                                                                                 +
     resource_exists INT;                                                                                                                                                                                                                                +
 BEGIN                                                                                                                                                                                                                                                   +
     -- Check if the resource exists                                                                                                                                                                                                                     +
     SELECT COUNT(*) INTO resource_exists FROM public.tlkresources WHERE i_res = resource_id;                                                                                                                                                            +
                                                                                                                                                                                                                                                         +
     IF resource_exists = 0 THEN                                                                                                                                                                                                                         +
         RAISE EXCEPTION 'Resource ID % not found.', resource_id;                                                                                                                                                                                        +
     END IF;                                                                                                                                                                                                                                             +
                                                                                                                                                                                                                                                         +
     -- Update the resource                                                                                                                                                                                                                              +
     UPDATE public.tlkresources                                                                                                                                                                                                                          +
     SET                                                                                                                                                                                                                                                 +
         i_typ_res = resource_type,                                                                                                                                                                                                                      +
         x_nm_res = resource_name,                                                                                                                                                                                                                       +
         x_ip = resource_ip,                                                                                                                                                                                                                             +
         i_prt = resource_port,                                                                                                                                                                                                                          +
         i_rnk = resource_rank,                                                                                                                                                                                                                          +
         f_fs = resource_fs,                                                                                                                                                                                                                             +
         f_avg = resource_avg                                                                                                                                                                                                                            +
     WHERE i_res = resource_id;                                                                                                                                                                                                                          +
 END;                                                                                                                                                                                                                                                    +
 $function$                                                                                                                                                                                                                                              +
 

Name: usp_resource_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resource_list()                                                                                                          +
  RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         r.i_res,                                                                                                                                               +
         r.i_typ_res,                                                                                                                                           +
         r.x_nm_res,                                                                                                                                            +
         r.x_ip,                                                                                                                                                +
         r.i_prt,                                                                                                                                               +
         r.i_rnk,                                                                                                                                               +
         r.f_fs,                                                                                                                                                +
         r.f_avg                                                                                                                                                +
     FROM public.tlkresources r;                                                                                                                                +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_resource_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resource_select_by_id(resource_id integer)                                                                               +
  RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         r.i_res,                                                                                                                                               +
         r.i_typ_res,                                                                                                                                           +
         r.x_nm_res,                                                                                                                                            +
         r.x_ip,                                                                                                                                                +
         r.i_prt,                                                                                                                                               +
         r.i_rnk,                                                                                                                                               +
         r.f_fs,                                                                                                                                                +
         r.f_avg                                                                                                                                                +
     FROM public.tlkresources r                                                                                                                                 +
     WHERE r.i_res = resource_id;                                                                                                                               +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_resource_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resource_type_list()    +
  RETURNS TABLE(i_typ_res integer, x_dsc_res character varying)+
  LANGUAGE plpgsql                                             +
 AS $function$                                                 +
 BEGIN                                                         +
     RETURN QUERY                                              +
     SELECT                                                    +
         t.i_typ_res,                                          +
         t.x_dsc_res  -- Corrected column name                 +
     FROM public.tlkresourcetypes t;                           +
 END;                                                          +
 $function$                                                    +
 

Name: usp_resource_type_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_add(resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean)+
  RETURNS integer                                                                                                                                                                                                                   +
  LANGUAGE plpgsql                                                                                                                                                                                                                  +
 AS $function$                                                                                                                                                                                                                      +
 DECLARE                                                                                                                                                                                                                            +
     new_resource_id INT;                                                                                                                                                                                                           +
 BEGIN                                                                                                                                                                                                                              +
     -- Insert the resource and return the new ID                                                                                                                                                                                   +
     INSERT INTO public.tlkresources (I_TYP_RES, X_NM_RES, X_IP, I_PRT, I_RNK, F_FS, F_AVG)                                                                                                                                         +
     VALUES (resource_type, resource_name, resource_ip, resource_port, resource_rank, resource_fs, resource_avg)                                                                                                                    +
     RETURNING I_RES INTO new_resource_id;                                                                                                                                                                                          +
                                                                                                                                                                                                                                    +
     -- Return the newly created resource ID                                                                                                                                                                                        +
     RETURN new_resource_id;                                                                                                                                                                                                        +
 END;                                                                                                                                                                                                                               +
 $function$                                                                                                                                                                                                                         +
 

Name: usp_resources_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_rank_down(resource_id integer)+
  RETURNS void                                                                 +
  LANGUAGE plpgsql                                                             +
 AS $function$                                                                 +
 BEGIN                                                                         +
     -- Update the resource rank by increasing `i_rnk` by 1                    +
     UPDATE public.tlkresources                                                +
     SET i_rnk = i_rnk + 1                                                     +
     WHERE i_res = resource_id;                                                +
 END;                                                                          +
 $function$                                                                    +
 

Name: usp_resources_rank_down\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_rank_up(resource_id integer)+
  RETURNS void                                                               +
  LANGUAGE plpgsql                                                           +
 AS $function$                                                               +
 BEGIN                                                                       +
     -- Update the resource rank by decreasing `i_rnk` by 1                  +
     UPDATE public.tlkresources                                              +
     SET i_rnk = i_rnk - 1                                                   +
     WHERE i_res = resource_id;                                              +
 END;                                                                        +
 $function$                                                                  +
 

Name: usp_resources_rank_up\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_select(resource_id integer)                                                                                    +
  RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         r.i_res,                                                                                                                                               +
         r.i_typ_res,                                                                                                                                           +
         r.x_nm_res,                                                                                                                                            +
         r.x_ip,                                                                                                                                                +
         r.i_prt,                                                                                                                                               +
         r.i_rnk,                                                                                                                                               +
         r.f_fs,                                                                                                                                                +
         r.f_avg                                                                                                                                                +
     FROM public.tlkresources r                                                                                                                                 +
     WHERE r.i_res = resource_id;                                                                                                                               +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_resources_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_select_all()                                                                                                   +
  RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         r.i_res,                                                                                                                                               +
         r.i_typ_res,                                                                                                                                           +
         r.x_nm_res,                                                                                                                                            +
         r.x_ip,                                                                                                                                                +
         r.i_prt,                                                                                                                                               +
         r.i_rnk,                                                                                                                                               +
         r.f_fs,                                                                                                                                                +
         r.f_avg                                                                                                                                                +
     FROM public.tlkresources r;                                                                                                                                +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_resources_select_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_resources_select_by_type(resource_type integer)                                                                          +
  RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)+
  LANGUAGE plpgsql                                                                                                                                              +
 AS $function$                                                                                                                                                  +
 BEGIN                                                                                                                                                          +
     RETURN QUERY                                                                                                                                               +
     SELECT                                                                                                                                                     +
         r.i_res,                                                                                                                                               +
         r.i_typ_res,                                                                                                                                           +
         r.x_nm_res,                                                                                                                                            +
         r.x_ip,                                                                                                                                                +
         r.i_prt,                                                                                                                                               +
         r.i_rnk,                                                                                                                                               +
         r.f_fs,                                                                                                                                                +
         r.f_avg                                                                                                                                                +
     FROM public.tlkresources r                                                                                                                                 +
     WHERE r.i_typ_res = resource_type;                                                                                                                         +
 END;                                                                                                                                                           +
 $function$                                                                                                                                                     +
 

Name: usp_resources_select_by_type\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_add(i_dir integer, x_nm_trg character varying, f_ign boolean)+
  RETURNS integer                                                                                           +
  LANGUAGE plpgsql                                                                                          +
 AS $function$                                                                                              +
                                                                                                            +
 DECLARE new_trigger_id INT;                                                                                +
                                                                                                            +
 BEGIN                                                                                                      +
     -- Ensure the trigger name does not already exist                                                      +
     IF EXISTS (SELECT 1 FROM public.triggers WHERE triggers.x_nm_trg = usp_trigger_add.x_nm_trg) THEN      +
         RAISE EXCEPTION 'Trigger name % already exists', x_nm_trg;                                         +
     END IF;                                                                                                +
                                                                                                            +
     -- Insert into triggers and return the new ID                                                          +
     INSERT INTO public.triggers (X_NM_TRG, I_DIR, F_IGN)                                                   +
     VALUES (usp_trigger_add.x_nm_trg, usp_trigger_add.i_dir, usp_trigger_add.f_ign)                        +
     RETURNING I_TRG INTO new_trigger_id;                                                                   +
                                                                                                            +
     -- Initialize state tracking in trigger_states table                                                   +
     INSERT INTO public.trigger_states (i_trg, x_id_dev, last_state)                                        +
     SELECT new_trigger_id, d.x_id_dev, 0 FROM public.devices d;                                            +
                                                                                                            +
     -- Log success                                                                                         +
     RAISE NOTICE 'Trigger Added: ID = %, Name = %, Direction = %, Ignore = %',                             +
         new_trigger_id, x_nm_trg, i_dir, f_ign;                                                            +
                                                                                                            +
     RETURN new_trigger_id;                                                                                 +
                                                                                                            +
 EXCEPTION                                                                                                  +
     WHEN unique_violation THEN                                                                             +
         RAISE EXCEPTION 'Trigger name % already exists', x_nm_trg;                                         +
     WHEN foreign_key_violation THEN                                                                        +
         RAISE EXCEPTION 'Direction ID % does not exist in tlktrigdirections', i_dir;                       +
     WHEN others THEN                                                                                       +
         RAISE EXCEPTION 'Unexpected error adding trigger: %', SQLERRM;                                     +
         RETURN -1;                                                                                         +
 END;                                                                                                       +
 $function$                                                                                                 +
 

Name: usp_trigger_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE PROCEDURE public.usp_trigger_add(IN p_x_nm_trg character varying, IN p_i_dir integer, IN p_i_zn integer, IN p_f_ign boolean, OUT p_i_trg integer)+
  LANGUAGE plpgsql                                                                                                                                                  +
 AS $procedure$                                                                                                                                                     +
 -- Name: usp_trigger_add                                                                                                                                           +
 -- Version: 0.1.57                                                                                                                                                 +
 -- Created: 971201                                                                                                                                                 +
 -- Modified: 250501                                                                                                                                                +
 -- Creator: ParcoAdmin                                                                                                                                             +
 -- Modified By: ParcoAdmin                                                                                                                                         +
 -- Description: Adds a new trigger to the triggers table and initializes state tracking                                                                            +
 -- Location: ParcoRTLSMaint                                                                                                                                        +
 -- Role: Database                                                                                                                                                  +
 -- Status: Active                                                                                                                                                  +
 -- Dependent: TRUE                                                                                                                                                 +
 BEGIN                                                                                                                                                              +
     -- Validate inputs                                                                                                                                             +
     RAISE NOTICE 'Received p_i_zn: %', p_i_zn;                                                                                                                     +
     IF p_i_zn IS NULL THEN                                                                                                                                         +
         RAISE EXCEPTION 'Zone ID cannot be NULL.';                                                                                                                 +
     END IF;                                                                                                                                                        +
     IF NOT EXISTS (SELECT 1 FROM zones WHERE i_zn = p_i_zn) THEN                                                                                                   +
         RAISE EXCEPTION 'Zone ID % does not exist.', p_i_zn;                                                                                                       +
     END IF;                                                                                                                                                        +
     IF NOT EXISTS (SELECT 1 FROM tlktrigdirections WHERE i_dir = p_i_dir) THEN                                                                                     +
         RAISE EXCEPTION 'Direction ID % does not exist.', p_i_dir;                                                                                                 +
     END IF;                                                                                                                                                        +
     IF EXISTS (SELECT 1 FROM triggers WHERE x_nm_trg = p_x_nm_trg) THEN                                                                                            +
         RAISE EXCEPTION 'Trigger name % already exists.', p_x_nm_trg;                                                                                              +
     END IF;                                                                                                                                                        +
                                                                                                                                                                    +
     -- Generate a new trigger ID                                                                                                                                   +
     SELECT nextval('seq_triggers') INTO p_i_trg;                                                                                                                   +
                                                                                                                                                                    +
     -- Insert the trigger                                                                                                                                          +
     RAISE NOTICE 'Inserting trigger with i_zn: %', p_i_zn;                                                                                                         +
     INSERT INTO triggers (i_trg, x_nm_trg, i_dir, i_zn, ignore_unknowns)                                                                                           +
     VALUES (p_i_trg, p_x_nm_trg, p_i_dir, p_i_zn, p_f_ign);                                                                                                        +
                                                                                                                                                                    +
     -- Initialize state tracking in trigger_states table (if devices exist)                                                                                        +
     RAISE NOTICE 'Checking for devices...';                                                                                                                        +
     IF EXISTS (SELECT 1 FROM devices) THEN                                                                                                                         +
         RAISE NOTICE 'Devices found, inserting into trigger_states for trigger ID %.', p_i_trg;                                                                    +
         INSERT INTO trigger_states (i_trg, x_id_dev, last_state)                                                                                                   +
         SELECT p_i_trg, d.x_id_dev, 0 FROM devices d;                                                                                                              +
         RAISE NOTICE 'Inserted % rows into trigger_states.', (SELECT COUNT(*) FROM trigger_states WHERE i_trg = p_i_trg);                                          +
     ELSE                                                                                                                                                           +
         RAISE NOTICE 'No devices found; trigger_states not initialized for trigger ID %.', p_i_trg;                                                                +
     END IF;                                                                                                                                                        +
                                                                                                                                                                    +
     -- Explicitly return the OUT parameter                                                                                                                         +
     SELECT p_i_trg INTO p_i_trg;                                                                                                                                   +
     RAISE NOTICE 'Trigger added successfully with ID %.', p_i_trg;                                                                                                 +
                                                                                                                                                                    +
 EXCEPTION                                                                                                                                                          +
     WHEN unique_violation THEN                                                                                                                                     +
         RAISE EXCEPTION 'Trigger name % already exists.', p_x_nm_trg;                                                                                              +
     WHEN foreign_key_violation THEN                                                                                                                                +
         IF SQLERRM LIKE '%zones%' THEN                                                                                                                             +
             RAISE EXCEPTION 'Zone ID % does not exist.', p_i_zn;                                                                                                   +
         ELSIF SQLERRM LIKE '%tlktrigdirections%' THEN                                                                                                              +
             RAISE EXCEPTION 'Direction ID % does not exist.', p_i_dir;                                                                                             +
         ELSE                                                                                                                                                       +
             RAISE EXCEPTION 'Foreign key violation: %', SQLERRM;                                                                                                   +
         END IF;                                                                                                                                                    +
     WHEN others THEN                                                                                                                                               +
         RAISE EXCEPTION 'Error adding trigger: %', SQLERRM;                                                                                                        +
 END;                                                                                                                                                               +
 $procedure$                                                                                                                                                        +
 

Name: usp_trigger_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_delete(trigger_id integer)                    +
  RETURNS boolean                                                                            +
  LANGUAGE plpgsql                                                                           +
 AS $function$  -- Return TRUE if deleted, FALSE if not found                                +
 DECLARE                                                                                     +
     deleted_count INT;                                                                      +
 BEGIN                                                                                       +
     -- Remove dependent entries in trigger_states first                                     +
     DELETE FROM public.trigger_states WHERE i_trg = trigger_id;                             +
                                                                                             +
     -- Delete the trigger                                                                   +
     DELETE FROM public.triggers WHERE i_trg = trigger_id RETURNING i_trg INTO deleted_count;+
                                                                                             +
     -- If nothing was deleted, return FALSE                                                 +
     IF deleted_count IS NULL THEN                                                           +
         RETURN FALSE;                                                                       +
     END IF;                                                                                 +
                                                                                             +
     RETURN TRUE;                                                                            +
 END;                                                                                        +
 $function$                                                                                  +
 

Name: usp_trigger_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_direction_list()+
  RETURNS TABLE(i_dir integer, x_dir character varying)        +
  LANGUAGE plpgsql                                             +
 AS $function$                                                 +
 BEGIN                                                         +
     RETURN QUERY                                              +
     SELECT t.i_dir, t.x_dir                                   +
     FROM public.tlktrigdirections t;                          +
 END;                                                          +
 $function$                                                    +
 

Name: usp_trigger_direction_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_edit(trigger_id integer, trigger_name character varying, trigger_dir integer, trigger_ignore boolean)+
  RETURNS void                                                                                                                                      +
  LANGUAGE plpgsql                                                                                                                                  +
 AS $function$                                                                                                                                      +
 DECLARE                                                                                                                                            +
     trigger_exists INT;                                                                                                                            +
 BEGIN                                                                                                                                              +
     -- Check if the trigger exists                                                                                                                 +
     SELECT COUNT(*) INTO trigger_exists FROM public.triggers WHERE i_trg = trigger_id;                                                             +
                                                                                                                                                    +
     IF trigger_exists = 0 THEN                                                                                                                     +
         RAISE EXCEPTION 'Trigger ID % not found.', trigger_id;                                                                                     +
     END IF;                                                                                                                                        +
                                                                                                                                                    +
     -- Update the trigger                                                                                                                          +
     UPDATE public.triggers                                                                                                                         +
     SET                                                                                                                                            +
         x_nm_trg = trigger_name,                                                                                                                   +
         i_dir = trigger_dir,                                                                                                                       +
         f_ign = trigger_ignore                                                                                                                     +
     WHERE i_trg = trigger_id;                                                                                                                      +
 END;                                                                                                                                               +
 $function$                                                                                                                                         +
 

Name: usp_trigger_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_list()                                   +
  RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean)+
  LANGUAGE plpgsql                                                                      +
 AS $function$                                                                          +
 BEGIN                                                                                  +
     RETURN QUERY                                                                       +
     SELECT                                                                             +
         t.i_trg,                                                                       +
         t.x_nm_trg,                                                                    +
         t.i_dir,                                                                       +
         t.f_ign                                                                        +
     FROM public.triggers t;                                                            +
 END;                                                                                   +
 $function$                                                                             +
 

Name: usp_trigger_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_move(trigger_id integer, new_x numeric, new_y numeric, new_z numeric)+
  RETURNS void                                                                                                      +
  LANGUAGE plpgsql                                                                                                  +
 AS $function$                                                                                                      +
                                                                                                                    +
 BEGIN                                                                                                              +
     -- Ensure trigger exists                                                                                       +
     IF NOT EXISTS (SELECT 1 FROM public.triggers WHERE i_trg = trigger_id) THEN                                    +
         RAISE EXCEPTION 'Trigger ID % does not exist', trigger_id;                                                 +
     END IF;                                                                                                        +
                                                                                                                    +
     -- Move the trigger by updating all related vertices                                                           +
     UPDATE public.vertices                                                                                         +
     SET n_x = n_x + new_x, n_y = n_y + new_y, n_z = n_z + new_z                                                    +
     WHERE i_rgn IN (SELECT i_rgn FROM public.regions WHERE i_trg = trigger_id);                                    +
                                                                                                                    +
     -- Log success                                                                                                 +
     RAISE NOTICE 'Trigger ID % moved by (%, %, %)', trigger_id, new_x, new_y, new_z;                               +
                                                                                                                    +
 END;                                                                                                               +
 $function$                                                                                                         +
 

Name: usp_trigger_move\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_select(trigger_id integer)                                                                                                                                             +
  RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                    +
 AS $function$                                                                                                                                                                                                        +
                                                                                                                                                                                                                      +
 BEGIN                                                                                                                                                                                                                +
     RETURN QUERY                                                                                                                                                                                                     +
     SELECT                                                                                                                                                                                                           +
         t.i_trg, t.x_nm_trg, t.i_dir, t.f_ign,                                                                                                                                                                       +
         r.i_rgn, r.i_zn, r.x_nm_rgn,                                                                                                                                                                                 +
         v.n_x, v.n_y, v.n_z, v.n_ord, v.i_vtx                                                                                                                                                                        +
     FROM public.triggers t                                                                                                                                                                                           +
     LEFT JOIN public.regions r ON t.i_trg = r.i_trg                                                                                                                                                                  +
     LEFT JOIN public.vertices v ON r.i_rgn = v.i_rgn                                                                                                                                                                 +
     WHERE t.i_trg = trigger_id;                                                                                                                                                                                      +
 END;                                                                                                                                                                                                                 +
 $function$                                                                                                                                                                                                           +
 

Name: usp_trigger_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_select_all()                                                                                                                                                           +
  RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                    +
 AS $function$                                                                                                                                                                                                        +
 BEGIN                                                                                                                                                                                                                +
     RETURN QUERY                                                                                                                                                                                                     +
     SELECT                                                                                                                                                                                                           +
         t.i_trg,                                                                                                                                                                                                     +
         t.x_nm_trg,                                                                                                                                                                                                  +
         t.i_dir,                                                                                                                                                                                                     +
         t.f_ign,                                                                                                                                                                                                     +
         r.i_rgn,                                                                                                                                                                                                     +
         r.i_zn,                                                                                                                                                                                                      +
         r.x_nm_rgn,                                                                                                                                                                                                  +
         v.n_x::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_y::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_z::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_ord,                                                                                                                                                                                                     +
         v.i_vtx                                                                                                                                                                                                      +
     FROM public.triggers t                                                                                                                                                                                           +
     LEFT OUTER JOIN public.regions r ON t.i_trg = r.i_trg                                                                                                                                                            +
     LEFT OUTER JOIN public.vertices v ON r.i_rgn = v.i_rgn;                                                                                                                                                          +
 END;                                                                                                                                                                                                                 +
 $function$                                                                                                                                                                                                           +
 

Name: usp_trigger_select_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_select_by_id(trigger_id integer)         +
  RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean)+
  LANGUAGE plpgsql                                                                      +
 AS $function$                                                                          +
 BEGIN                                                                                  +
     RETURN QUERY                                                                       +
     SELECT                                                                             +
         t.i_trg,                                                                       +
         t.x_nm_trg,                                                                    +
         t.i_dir,                                                                       +
         t.f_ign                                                                        +
     FROM public.triggers t                                                             +
     WHERE t.i_trg = trigger_id;                                                        +
 END;                                                                                   +
 $function$                                                                             +
 

Name: usp_trigger_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_trigger_select_by_point(point_x numeric, point_y numeric, point_z numeric)                                                                                                     +
  RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)+
  LANGUAGE plpgsql                                                                                                                                                                                                    +
 AS $function$                                                                                                                                                                                                        +
 BEGIN                                                                                                                                                                                                                +
     RETURN QUERY                                                                                                                                                                                                     +
     SELECT                                                                                                                                                                                                           +
         t.i_trg,                                                                                                                                                                                                     +
         t.x_nm_trg,                                                                                                                                                                                                  +
         t.i_dir,                                                                                                                                                                                                     +
         t.f_ign,                                                                                                                                                                                                     +
         r.i_rgn,                                                                                                                                                                                                     +
         r.i_zn,                                                                                                                                                                                                      +
         r.x_nm_rgn,                                                                                                                                                                                                  +
         v.n_x::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_y::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_z::NUMERIC(18,2),                                                                                                                                                                                        +
         v.n_ord,                                                                                                                                                                                                     +
         v.i_vtx                                                                                                                                                                                                      +
     FROM public.triggers t                                                                                                                                                                                           +
     LEFT OUTER JOIN public.regions r ON t.i_trg = r.i_trg                                                                                                                                                            +
     LEFT OUTER JOIN public.vertices v ON r.i_rgn = v.i_rgn                                                                                                                                                           +
     WHERE r.n_max_x >= point_x AND r.n_min_x <= point_x                                                                                                                                                              +
     AND r.n_max_y >= point_y AND r.n_min_y <= point_y                                                                                                                                                                +
     AND r.n_max_z >= point_z AND r.n_min_z <= point_z;                                                                                                                                                               +
 END;                                                                                                                                                                                                                 +
 $function$                                                                                                                                                                                                           +
 

Name: usp_trigger_select_by_point\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_vertex_add(p_i_rgn integer, p_n_x real, p_n_y real, p_n_z real, p_n_ord integer)+
  RETURNS integer                                                                                                      +
  LANGUAGE plpgsql                                                                                                     +
 AS $function$                                                                                                         +
 DECLARE                                                                                                               +
     v_i_vtx INTEGER;                                                                                                  +
 BEGIN                                                                                                                 +
     INSERT INTO vertices (i_rgn, n_x, n_y, n_z, n_ord)                                                                +
     VALUES (p_i_rgn, p_n_x, p_n_y, p_n_z, p_n_ord)                                                                    +
     RETURNING i_vtx INTO v_i_vtx;                                                                                     +
     RETURN v_i_vtx;                                                                                                   +
 END;                                                                                                                  +
 $function$                                                                                                            +
 

Name: usp_vertex_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_vertex_delete(vertex_id integer)              +
  RETURNS void                                                                       +
  LANGUAGE plpgsql                                                                   +
 AS $function$                                                                       +
 DECLARE                                                                             +
     vertex_exists INT;                                                              +
 BEGIN                                                                               +
     -- Check if the vertex exists                                                   +
     SELECT COUNT(*) INTO vertex_exists FROM public.vertices WHERE i_vtx = vertex_id;+
                                                                                     +
     IF vertex_exists = 0 THEN                                                       +
         RAISE EXCEPTION 'Vertex ID % not found.', vertex_id;                        +
     END IF;                                                                         +
                                                                                     +
     -- Perform the delete operation                                                 +
     DELETE FROM public.vertices WHERE i_vtx = vertex_id;                            +
 END;                                                                                +
 $function$                                                                          +
 

Name: usp_vertex_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_vertex_edit(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer)+
  RETURNS void                                                                                                                                       +
  LANGUAGE plpgsql                                                                                                                                   +
 AS $function$                                                                                                                                       +
 DECLARE                                                                                                                                             +
     vertex_exists INT;                                                                                                                              +
 BEGIN                                                                                                                                               +
     -- Check if the vertex exists                                                                                                                   +
     SELECT COUNT(*) INTO vertex_exists FROM public.vertices WHERE i_vtx = vertex_id;                                                                +
                                                                                                                                                     +
     IF vertex_exists = 0 THEN                                                                                                                       +
         RAISE EXCEPTION 'Vertex ID % not found.', vertex_id;                                                                                        +
     END IF;                                                                                                                                         +
                                                                                                                                                     +
     -- Update the vertex                                                                                                                            +
     UPDATE public.vertices                                                                                                                          +
     SET                                                                                                                                             +
         n_x = coord_x,                                                                                                                              +
         n_y = coord_y,                                                                                                                              +
         n_z = coord_z,                                                                                                                              +
         n_ord = order_num,                                                                                                                          +
         i_rgn = region_id                                                                                                                           +
     WHERE i_vtx = vertex_id;                                                                                                                        +
 END;                                                                                                                                                +
 $function$                                                                                                                                          +
 

Name: usp_vertex_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_vertex_list()                                      +
  RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)+
  LANGUAGE plpgsql                                                                        +
 AS $function$                                                                            +
 BEGIN                                                                                    +
     RETURN QUERY                                                                         +
     SELECT                                                                               +
         v.i_vtx,                                                                         +
         v.n_x,                                                                           +
         v.n_y,                                                                           +
         v.n_z,                                                                           +
         v.n_ord,                                                                         +
         v.i_rgn                                                                          +
     FROM public.vertices v;                                                              +
 END;                                                                                     +
 $function$                                                                               +
 

Name: usp_vertex_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_vertex_select_by_id(vertex_id integer)             +
  RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)+
  LANGUAGE plpgsql                                                                        +
 AS $function$                                                                            +
 BEGIN                                                                                    +
     RETURN QUERY                                                                         +
     SELECT                                                                               +
         v.i_vtx,                                                                         +
         v.n_x,                                                                           +
         v.n_y,                                                                           +
         v.n_z,                                                                           +
         v.n_ord,                                                                         +
         v.i_rgn                                                                          +
     FROM public.vertices v                                                               +
     WHERE v.i_vtx = vertex_id;                                                           +
 END;                                                                                     +
 $function$                                                                               +
 

Name: usp_vertex_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_add(i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  RETURNS integer                                                                                             +
  LANGUAGE plpgsql                                                                                            +
 AS $function$                                                                                                +
 DECLARE                                                                                                      +
     new_zone_id INT;                                                                                         +
 BEGIN                                                                                                        +
     -- Insert into zones and return the new ID                                                               +
     INSERT INTO public.zones (I_TYP_ZN, X_NM_ZN, I_PNT_ZN)                                                   +
     VALUES (i_typ_zn, x_nm_zn, i_pnt_zn)                                                                     +
     RETURNING I_ZN INTO new_zone_id;                                                                         +
                                                                                                              +
     -- Return the newly created zone ID                                                                      +
     RETURN new_zone_id;                                                                                      +
 END;                                                                                                         +
 $function$                                                                                                   +
 

Name: usp_zone_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_children_select(parent_zone_id integer)         +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 BEGIN                                                                                      +
     RETURN QUERY                                                                           +
     SELECT                                                                                 +
         z.I_ZN,                                                                            +
         z.I_TYP_ZN,                                                                        +
         z.X_NM_ZN,                                                                         +
         z.I_PNT_ZN                                                                         +
     FROM public.zones z                                                                    +
     WHERE z.I_PNT_ZN = parent_zone_id;                                                     +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_children_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_delete(i_zn integer)             +
  RETURNS integer                                                            +
  LANGUAGE plpgsql                                                           +
 AS $function$                                                               +
 DECLARE                                                                     +
     delete_error INT := 0;                                                  +
 BEGIN                                                                       +
     -- Perform the delete operation                                         +
     DELETE FROM public.zones WHERE public.zones.I_ZN = usp_zone_delete.i_zn;+
                                                                             +
     -- Capture error code (0 means success, 1 means failure)                +
     GET DIAGNOSTICS delete_error = ROW_COUNT;                               +
                                                                             +
     -- If no rows were deleted, return 1 (like MSSQL's @@ERROR)             +
     IF delete_error = 0 THEN                                                +
         RETURN 1;                                                           +
     END IF;                                                                 +
                                                                             +
     -- Otherwise, return success                                            +
     RETURN 0;                                                               +
 END;                                                                        +
 $function$                                                                  +
 

Name: usp_zone_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_edit(p_zn_id integer, p_typ_zn integer, p_nm_zn character varying, p_pnt_zn integer DEFAULT NULL::integer)+
  RETURNS integer                                                                                                                                     +
  LANGUAGE plpgsql                                                                                                                                    +
 AS $function$                                                                                                                                        +
 DECLARE                                                                                                                                              +
     zone_exists INT;                                                                                                                                 +
 BEGIN                                                                                                                                                +
     -- Check if the zone exists                                                                                                                      +
     SELECT COUNT(*) INTO zone_exists                                                                                                                 +
     FROM public.zones r                                                                                                                              +
     WHERE r.I_ZN = p_zn_id;  -- ✅ No ambiguity                                                                                                      +
                                                                                                                                                      +
     IF zone_exists = 0 THEN                                                                                                                          +
         RAISE EXCEPTION 'Zone ID not found: %', p_zn_id;                                                                                             +
     END IF;                                                                                                                                          +
                                                                                                                                                      +
     -- Check for a zone specifying itself as a parent                                                                                                +
     IF p_zn_id = p_pnt_zn THEN                                                                                                                       +
         RAISE EXCEPTION 'A Zone may not specify itself as its parent';                                                                               +
     END IF;                                                                                                                                          +
                                                                                                                                                      +
     -- Update the zone                                                                                                                               +
     UPDATE public.zones                                                                                                                              +
     SET                                                                                                                                              +
         I_TYP_ZN = p_typ_zn,                                                                                                                         +
         X_NM_ZN = p_nm_zn,                                                                                                                           +
         I_PNT_ZN = p_pnt_zn                                                                                                                          +
     WHERE I_ZN = p_zn_id;  -- ✅ No ambiguity                                                                                                        +
                                                                                                                                                      +
     -- Return 0 for success                                                                                                                          +
     RETURN 0;                                                                                                                                        +
 END;                                                                                                                                                 +
 $function$                                                                                                                                           +
 

Name: usp_zone_edit\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_list()                                          +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 BEGIN                                                                                      +
     RETURN QUERY                                                                           +
     SELECT                                                                                 +
         z.I_ZN,                                                                            +
         z.I_TYP_ZN,                                                                        +
         z.X_NM_ZN,                                                                         +
         z.I_PNT_ZN                                                                         +
     FROM public.zones z;                                                                   +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_parent_select(child_zone_id integer)            +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 DECLARE                                                                                    +
     parent_zone_id INT;                                                                    +
 BEGIN                                                                                      +
     -- Get the parent zone ID                                                              +
     SELECT z.I_PNT_ZN INTO parent_zone_id                                                  +
     FROM public.zones z                                                                    +
     WHERE z.I_ZN = child_zone_id;                                                          +
                                                                                            +
     -- Ensure parent_zone_id is NOT NULL before querying                                   +
     IF parent_zone_id IS NOT NULL THEN                                                     +
         RETURN QUERY                                                                       +
         SELECT                                                                             +
             z.I_ZN,                                                                        +
             z.I_TYP_ZN,                                                                    +
             z.X_NM_ZN,                                                                     +
             z.I_PNT_ZN                                                                     +
         FROM public.zones z                                                                +
         WHERE z.I_ZN = parent_zone_id;                                                     +
     END IF;                                                                                +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_parent_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_select(zone_id integer)                         +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 BEGIN                                                                                      +
     RETURN QUERY                                                                           +
     SELECT                                                                                 +
         z.I_ZN,                                                                            +
         z.I_TYP_ZN,                                                                        +
         z.X_NM_ZN,                                                                         +
         z.I_PNT_ZN                                                                         +
     FROM public.zones z                                                                    +
     WHERE z.I_ZN = zone_id;                                                                +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_select\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_select_all()                                    +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 BEGIN                                                                                      +
     RETURN QUERY                                                                           +
     SELECT                                                                                 +
         z.I_ZN,                                                                            +
         z.I_TYP_ZN,                                                                        +
         z.X_NM_ZN,                                                                         +
         z.I_PNT_ZN                                                                         +
     FROM public.zones z;                                                                   +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_select_all\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_select_by_id(zone_id integer)                   +
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)+
  LANGUAGE plpgsql                                                                          +
 AS $function$                                                                              +
 BEGIN                                                                                      +
     RETURN QUERY                                                                           +
     SELECT                                                                                 +
         z.i_zn,                                                                            +
         z.i_typ_zn,                                                                        +
         z.x_nm_zn,                                                                         +
         z.i_pnt_zn                                                                         +
     FROM public.zones z                                                                    +
     WHERE z.i_zn = zone_id;                                                                +
 END;                                                                                       +
 $function$                                                                                 +
 

Name: usp_zone_select_by_id\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_select_by_point(point_x numeric, point_y numeric, point_z numeric)+
  RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)                  +
  LANGUAGE plpgsql                                                                                            +
 AS $function$                                                                                                +
 BEGIN                                                                                                        +
     RETURN QUERY                                                                                             +
     SELECT                                                                                                   +
         z.I_ZN,                                                                                              +
         z.I_TYP_ZN,                                                                                          +
         z.X_NM_ZN,                                                                                           +
         z.I_PNT_ZN                                                                                           +
     FROM public.zones z                                                                                      +
     JOIN public.regions r ON z.I_ZN = r.I_ZN                                                                 +
     WHERE r.n_max_x >= point_x AND r.n_min_x <= point_x                                                      +
       AND r.n_max_y >= point_y AND r.n_min_y <= point_y                                                      +
       AND r.n_max_z >= point_z AND r.n_min_z <= point_z;                                                     +
 END;                                                                                                         +
 $function$                                                                                                   +
 

Name: usp_zone_select_by_point\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_type_add(zone_type_name character varying)+
  RETURNS integer                                                                     +
  LANGUAGE plpgsql                                                                    +
 AS $function$                                                                        +
 DECLARE                                                                              +
     new_zone_type_id INT;                                                            +
 BEGIN                                                                                +
     -- Insert new zone type and return its ID                                        +
     INSERT INTO public.tlkzonetypes (X_DSC_ZN)  -- ✅ Fixed column name              +
     VALUES (zone_type_name)                                                          +
     RETURNING I_TYP_ZN INTO new_zone_type_id;                                        +
                                                                                      +
     -- Return the newly created zone type ID                                         +
     RETURN new_zone_type_id;                                                         +
 END;                                                                                 +
 $function$                                                                           +
 

Name: usp_zone_type_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_vertices_add(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer)+
  RETURNS void                                                                                                                                             +
  LANGUAGE plpgsql                                                                                                                                         +
 AS $function$                                                                                                                                             +
 BEGIN                                                                                                                                                     +
     INSERT INTO public.vertices (i_vtx, n_x, n_y, n_z, n_ord, i_rgn)                                                                                      +
     VALUES (                                                                                                                                              +
         COALESCE(vertex_id, nextval('vertices_i_vtx_seq'::regclass)),                                                                                     +
         coord_x, coord_y, coord_z, order_num, region_id                                                                                                   +
     );                                                                                                                                                    +
 EXCEPTION                                                                                                                                                 +
     WHEN OTHERS THEN                                                                                                                                      +
         RAISE EXCEPTION 'Error in usp_zone_vertices_add: %', SQLERRM;                                                                                     +
 END;                                                                                                                                                      +
 $function$                                                                                                                                                +
 

Name: usp_zone_vertices_add\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_vertices_delete(zone_id integer) +
  RETURNS void                                                               +
  LANGUAGE plpgsql                                                           +
 AS $function$                                                               +
 DECLARE                                                                     +
     zone_exists INT;                                                        +
 BEGIN                                                                       +
     -- Check if the zone exists                                             +
     SELECT COUNT(*) INTO zone_exists FROM public.zones WHERE i_zn = zone_id;+
                                                                             +
     IF zone_exists = 0 THEN                                                 +
         RAISE EXCEPTION 'Zone ID % not found.', zone_id;                    +
     END IF;                                                                 +
                                                                             +
     -- Perform the delete operation (delete all vertices tied to the zone)  +
     DELETE FROM public.vertices WHERE i_rgn = zone_id;                      +
 END;                                                                        +
 $function$                                                                  +
 

Name: usp_zone_vertices_delete\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_vertices_list(zone_id integer)                +
  RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)+
  LANGUAGE plpgsql                                                                        +
 AS $function$                                                                            +
 BEGIN                                                                                    +
     RETURN QUERY                                                                         +
     SELECT                                                                               +
         v.i_vtx,                                                                         +
         v.n_x,                                                                           +
         v.n_y,                                                                           +
         v.n_z,                                                                           +
         v.n_ord,                                                                         +
         v.i_rgn                                                                          +
     FROM public.vertices v                                                               +
     WHERE v.i_rgn = zone_id;                                                             +
 END;                                                                                     +
 $function$                                                                               +
 

Name: usp_zone_vertices_list\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_vertices_select_by_region(region_id integer)  +
  RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)+
  LANGUAGE plpgsql                                                                        +
 AS $function$                                                                            +
 BEGIN                                                                                    +
     RETURN QUERY                                                                         +
     SELECT                                                                               +
         v.i_vtx,                                                                         +
         v.n_x,                                                                           +
         v.n_y,                                                                           +
         v.n_z,                                                                           +
         v.n_ord,                                                                         +
         v.i_rgn                                                                          +
     FROM public.vertices v                                                               +
     WHERE v.i_rgn = region_id;                                                           +
 END;                                                                                     +
 $function$                                                                               +
 

Name: usp_zone_vertices_select_by_region\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

 CREATE OR REPLACE FUNCTION public.usp_zone_vertices_select_by_zone(zone_id integer)                    +
  RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer, i_zn integer)+
  LANGUAGE plpgsql                                                                                      +
 AS $function$                                                                                          +
 BEGIN                                                                                                  +
     RETURN QUERY                                                                                       +
     SELECT                                                                                             +
         v.i_vtx,                                                                                       +
         v.n_x,                                                                                         +
         v.n_y,                                                                                         +
         v.n_z,                                                                                         +
         v.n_ord,                                                                                       +
         v.i_rgn,                                                                                       +
         r.i_zn  -- Fetch the zone ID from regions                                                      +
     FROM public.vertices v                                                                             +
     JOIN public.regions r ON v.i_rgn = r.i_rgn                                                         +
     WHERE r.i_zn = zone_id;                                                                            +
 END;                                                                                                   +
 $function$                                                                                             +
 

Name: usp_zone_vertices_select_by_zone\nVersion: 0.1.0\nCreated: 971201\nModified: 250503\nCreator: ParcoAdmin\nModified By: ParcoAdmin\nDescription: PROCEDURE in ParcoRTLSMaint database\nLocation: ParcoRTLSMaint\nRole: Database\nStatus: Active\nDependent: TRUE

