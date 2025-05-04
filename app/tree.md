/home/parcoadmin/parco_fastapi/app
├── 01-devstop.sh
├── 02-shutdownmenu.sh
├── 03-checkports.sh
├── 04-cleanstart.sh
├── 05-devcheck.sh
├── 06-devsession.sh
├── 07-setup.sh
├── 08-showtree.sh
├── 09-update.sh
├── 10-utilitymenu.sh
├── 11-shutdown.sh
├── 12-start_frontend.sh
├── 13-syncmenu.sh
├── 14-gitdiff.sh
├── 15-rebuild_stuff.sh
├── 16-htop.sh
├── 17-top.sh
├── 18-ps.sh
├── 19-update-component-versions.sh
├── api_modules
│   ├── building_l3.py
│   ├── building_outside_l2.py
│   ├── campus_l1.py
│   ├── database.log
│   ├── database.py
│   ├── db_connection.log
│   ├── door_l6.py
│   ├── elevator_l4.py
│   ├── floor_l4.py
│   ├── get_map_metadata.py
│   ├── get_map.py
│   ├── get_maps.py
│   ├── get_parent_zones.py
│   ├── get_zone_data_l3.py
│   ├── hallway_l6.py
│   ├── room_l6.py
│   ├── ui_building_outside_l2.py
│   ├── ui_campus_l1.py
│   ├── upload_map_coordinates.py
│   └── wing_l5.py
├── app_backup.py
├── app.py
├── build
│   └── favicon.ico
├── campus_225_map.png
├── components.json
├── config.py
├── database
│   ├── db_functions.py
│   ├── db.py
├── db
│   └── PostgresQL_ALLDBs_backup.sql
├── db_connection_pac.py
├── db_connection.py
├── detect_ports.py
├── docs
│   ├── entity_creation_notes.md
│   ├── fastapi_entity_notes.md
│   └── websocket_protocol.md
├── entity_models.py
├── favicon.ico
├── fetch_vertices.py
├── fetch_vertices_to_svg.py
├── file_list.txt
├── flask_debug.log
├── flask_log.txt
├── gitdiff.sh
├── .gitignore
├── manager
│   ├── data_processor.py
│   ├── datastream.py
│   ├── enums.py
│   ├── events.py
│   ├── fastapi_service.py
│   ├── manager.py
│   ├── models.py
│   ├── portable_trigger.py
│   ├── region.py
│   ├── sdk_client.py
│   ├── simulator.py
│   ├── test_client.py
│   ├── trigger.py
│   ├── utils.py
│   └── websocket.py
├── manager_250430.log
├── map26.png
├── map.svg
├── map_upload.py
├── map_zone_337.PNG
├── models.py
├── node_modules
├── old_app.py
├── package.backup.json
├── package.bak
├── package.json
├── package-lock.json
├── parco_Functions_pac.py
├── ParcoRTLS_Manual.md
├── process_mapper.log
├── psql.sh
├── public
│   ├── favicon.ico
│   └── index.html
├── requirements.txt
├── routes
│   ├── device.py
│   ├── entity.py
│   ├── favicon.ico
│   ├── history.py
│   ├── input.py
│   ├── maps.py
│   ├── maps_upload.py
│   ├── region.py
│   ├── text.py
│   ├── trigger.py
│   ├── vertex.py
│   ├── zone_builder copy.py
│   ├── zone_builder.py
│   ├── zonebuilder_routes.py
│   ├── zone.py
│   └── zoneviewer_routes.py
├── scaling_tool.py
├── scripts
│   ├── crontab_detect_ports
│   ├── detect_ports.py
│   ├── get_service_name.log
│   ├── get_service_name.py
│   ├── process_mapper.py
│   └── zone_mapper.py
├── src
│   ├── campusMapLoader.js
│   ├── campusMapLoader_pac.js
│   ├── components
│   │   ├── BuildOutTool.js
│   │   ├── CreateTrigger.js
│   │   ├── EntityMap.css
│   │   ├── EntityMap.js
│   │   ├── EntityMergeDemo.js
│   │   ├── MapBuildOut.js
│   │   ├── Map.css
│   │   ├── Map.js
│   │   ├── MapList.js
│   │   ├── MapPreview.js
│   │   ├── MapUpload.js
│   │   ├── MapZoneBuilder.js
│   │   ├── MapZoneViewer.js
│   │   ├── NewTriggerDemo.bak.js
│   │   ├── NewTriggerDemo.js
│   │   ├── NewTriggerViewer.js
│   │   ├── TriggerUX2025.jsx
│   │   ├── ZoneBuilder.css
│   │   ├── ZoneBuilder.js
│   │   └── ZoneViewer.js
│   ├── hooks
│   │   └── useFetchData.js
│   ├── index.js
│   ├── lib
│   │   └── utils
│   ├── SupportAccess.js
│   ├── TriggerDemo.css
│   └── TriggerDemo.js
├── static
│   ├── campusMapLoader.js
│   ├── campusMapLoader_pac.js
│   ├── default_grid_box_orig.png
│   ├── default_grid_box.png
│   ├── drawingTool.js
│   ├── drawingTool_pac.js
│   ├── favicon.ico
│   ├── mapLoader.js
│   ├── mapLoader_pac.js
│   ├── runonce.py
│   ├── vertexFormatter.js
│   ├── vertexFormatterL3.js
│   ├── vertexFormatterMap.js
│   ├── zone_editor_ui.js
│   ├── zoneManager.js
│   └── zoneManager_pac.js
├── templates
│   ├── archives and backups
│   │   ├── _building_l3.html
│   │   ├── zonebuilder_ui.html
│   │   └── zonebuilder_ui_l3.html
│   ├── base.html
│   ├── _building_l3.html
│   ├── _building_outside_l2.html
│   ├── _campus_l1.html
│   ├── default_map.html
│   ├── edit.html
│   ├── edit_map.html
│   ├── favicon.ico
│   ├── _floor_l4.html
│   ├── input_screen.html
│   ├── manage_default_map.html
│   ├── _map_selection.html
│   ├── _room_l6.html
│   ├── scaling_tool.html
│   ├── scaling_upload.html
│   ├── upload.html
│   ├── _wing_l5.html
│   ├── zonebuilder_ui.html
│   ├── zonebuilder_ui_pac.html
│   ├── zone_editor_ui.html
│   ├── zoneviewer_ui.html
│   └── zoneviewer_ui_pac.html
├── test_client.py
├── test_db_connection.py
├── test_db.py
├── test_map_17.png
├── test_map_19.png
├── test_map_235.png
├── test_map.png
├── test_parco_functions.py
├── tests
│   ├── test_api.py
│   ├── test_db.py
│   └── test_triggers.py
├── test_update_vertices.py
├── tmux_frontend.log
├── tools
│   ├── cleanup_test_data.log
│   └── cleanup_test_data.py
├── tree.md
├── uploaded_maps
├── uploads
├── utils.py
├── uvicorn.log
├── venv.sh
├── zonebuilder_api.log
├── zonebuilder_api_pac.py
├── zonebuilder_api.py
├── zoneviewer_api_pac.py
└── zoneviewer_api.py


