//this is a sample file only to show a way of generating nagios settings json that the plugins accept

define([], function() {
    var obj = {
        NagiosPlugins: {
            formContentTemplate: _.template('<form class="form form-horizontal" data-setting-name="<%= settingName %>"><% if(allowMultiple) { %> <i class="fa fa-times"></i> # } #<fieldset><%= content %><style scoped="scoped">.form-horizontal .form-group {margin-right: 0px;margin-left: 0px; }</style></fieldset></form>'),
            inputStringTemplate: _.template(
                '<div class="form-group">'+
                    '<label for="<%= name %>" class="col-sm-4 control-label"><%= label %></label>'+
                    '<div class="col-sm-3">'+
                        '<input type="text" <%if(warning===true) {%> style="border-color: #ffa800" <%} else if(critical===true) {%> style="border-color: #8a3104" <%} class="input-sm form-control" name="<%= name %>" id="<%= id %>" value="<%= typeof value !== "undefined" ? value : "" %>">'+
                    '</div>'+
                '</div>'),
            inputNumberTemplate: _.template(
            '<div class="form-group">'+
                '<label for="<%= name %>" class="col-sm-4 control-label"><%= label %></label>'+
                '<div class="col-sm-3">'+
                    '<input type="number" <%if(warning===true) {%> style="border-color: #ffa800" <%} else if(critical===true) {%> style="border-color: #8a3104" class="input-sm form-control" name="<%= name %>" id="<%= id %>" value="<%= typeof value !== "undefined" ? value : "" %>">'+
                '</div>'+
            '</div>'),
            inputAdvancedNumberTemplate: _.template(
            '<div class="form-group">'+
                '<label for="<%= name %>" class="col-sm-4 control-label"><%= label %></label>'+
                '<div class="col-sm-3">'+
                    '<input type="number" class="input-sm form-control" style="border-color: #ffa800" name="<%= name %>.warning" id="warning_<%= id %>" value=<%= typeof value !== "undefined" ? value.warning : "" %>>'+
                '</div>'+
                '<div class="col-sm-3">'+
                    '<input type="number" class="input-sm form-control" style="border-color: #8a3104" name="<%= name %>.critical" id="critical_<%= id %>" value="<%= typeof value !== "undefined" ? value.critical : "" %>">'+
                '</div>'+
                '<% if(typeof value.check_type !== "undefined") { %> <input type="hidden" name="<%= name %>.check_type" value="<%= value.check_type %>"> <% } %>'+
            '</div>'),
            inputSelectTemplate: _.template(
            '<div class="form-group">'+
                '<label class="col-sm-4 control-label" for="<%= name %>"><%= label %></label>'+
                '<div class="col-sm-4">'+
                    '<select name="<%= name %>" class="input-sm form-control"><% for(var i = 0; i < data.length; i++) { %> <option <%if(data[i] == value) { %> selected="selected" %< } %>><%= data[i] %></option> <% } %></select>'+
                '</div>'+
            '</div>'),
            getFieldLabel: function(fieldName, fieldValue) {
                if($.type(fieldValue) === 'string') {
                    return fieldName;
                }
                else if($.type(fieldValue) === 'object') {
                    if($.type(fieldValue.label) === 'string') {
                        return fieldValue.label;
                    }
                    else {
                        return fieldName;
                    }
                }
            },
            getFieldType: function(fieldValue) {
                if($.type(fieldValue) === 'string') {
                    if(fieldValue === 'int') return 'number';
                    if(fieldValue === 'string') return 'string';
                }
                else if($.type(fieldValue) === 'array') {
                    return 'select';
                }
                else if($.type(fieldValue) === 'object') {
                    if(fieldValue.type === 'int' && (fieldValue.simple === true || $.type(fieldValue.check_type) === 'undefined')) return 'number';
                    if(fieldValue.type === 'int') return 'advanced_number';
                    if(fieldValue.type === 'string' && (fieldValue.simple === true || $.type(fieldValue.check_type) === 'undefined')) return 'string';
                    if(fieldValue.type === 'string') return 'advanced_string';
                    if(fieldValue.type === 'array') return 'select';
                    if($.type(fieldValue.data) === 'array') return 'select';
                }
            },
            constructInput: function(fieldName, fieldValue, value) {
                var input = '';

                var fieldType = this.getFieldType(fieldValue);
                var fieldLabel = this.getFieldLabel(fieldName, fieldValue);

                var warning = false;
                var critical = false;

                if($.type(fieldValue.warning) !== 'undefined') {
                    warning = fieldValue.warning;
                }

                if($.type(fieldValue.critical) !== 'undefined') {
                    critical = fieldValue.critical;
                }

                var data = {label: fieldLabel, name: fieldName, id: fieldName, value: value, warning: warning, critical: critical};

                if (fieldType === 'number') {
                    input += this.inputNumberTemplate(data);
                }
                if (fieldType === 'string') {
                    input += this.inputStringTemplate(data);
                }
                else if (fieldType === 'select') {
                    input += this.inputSelectTemplate({label: fieldLabel, name: fieldName, data: fieldValue.data, value: value});
                }
                else if(fieldType === 'advanced_number') {
                    input += this.inputAdvancedNumberTemplate(data);
                }

                return input;
            },
            constructForm: function(configObject, currentValues) {
                var html = '';

                if(typeof currentValues === 'undefined') {
                    currentValues = {};
                }

                for (var key in configObject) {
                    if (configObject.hasOwnProperty(key)) {

                        //check if the specified config is a complex object ( advanced_number template )
                        if($.type(configObject[key]) === 'object' && typeof configObject[key].check_type !== 'undefined') {
                            if(typeof currentValues[key] === 'undefined') {
                                currentValues[key] = {};
                            }

                            if(typeof currentValues[key].check_type === 'undefined') {
                                currentValues[key].check_type = configObject[key].check_type;
                            }
                        }

                        html += this.constructInput(key, configObject[key], currentValues[key]);
                    }
                }

                return html;
            },
            saveNagiosSettings: function(e) {
                var json = {};
                var nodeId = $('#node-id').val();

                function isObjectEmpty(obj) {
                    var hasData = false;
                    for (var key in obj) {
                        if (obj.hasOwnProperty(key)) {
                            for (var valueKey in obj[key]) {
                                if (obj[key].hasOwnProperty(valueKey)) {
                                    if (valueKey !== 'check_type') {
                                        hasData = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    return hasData;
                }

                var forms = $('#your-form');
                $.each(forms, function(index, form) {
                    var obj = $(form).toObject();

                    if(!isObjectEmpty(obj)) return;

                    var formName = form.dataset.settingName;
                    if(typeof json[formName] === 'undefined') {
                        json[formName] = [obj];
                    } else if($.isArray(json[formName])) {
                        json[formName].push(obj);
                    }
                });

                $.ajax({
                    url: "url to your server",
                    type: "POST",
                    crossDomain: true,
                    data: {json: JSON.stringify({settings: json, nodeId: nodeId})},
                    dataType: "json",
                    success:function(result){
                        //sucess
                    },
                    error:function(xhr,status,error){
                        alert(status);
                    }
                });
            },
            addNagiosSettingsForm: function() {
                var nodeId = $('#node-id').val();

                var settingsName = $('#config-settings-value').val();
                var appendTo = $('#append-to-element');

                var config = obj.Config[settingsName];
                if(config.allow_multiple) {
                    var formFields = this.constructForm(config, {});
                    var form = this.formContentTemplate({content: formFields, settingName: settingsName, allowMultiple: config.allow_multiple});
                    var currentContentElement = $('#'+appendTo);

                    if(currentContentElement.find('form').length > 0) {
                        currentContentElement.append('<hr>');
                    }

                    currentContentElement.append(form);
                }
            },
            removeNagiosSettingsForm: function(e) {
                var target = $(e.currentTarget);

                var form = target.closest('form');
                form.remove();
            }
        },
        Config: {
            //{"traffic":[{"itfIndex":8,"min":0,"max":5000000,"type":"OUT"},{"itfIndex":9,"min":0,"max":5000000,"type":"OUT"}],"port":[{"itfIndex":8,"oper_status":1}]}
            "bgp": {
                "remote_ip": { label: "IP", type: "string", simple: true },
                "warning": { label: "Warning", type: "int", warning: true },
                "critical": { label: "Critical", type: "int", critical: true },
                "allow_multiple": false
            },
            "traffic": {
                "itfIndex": { label: "Interface index", type: "int", simple: true },
                "min": { label: "Min (Kbps)", type: "int", simple: true, critical: true },
                "max": { label: "Max (Kbps)", type: "int", simple: true, critical: true },
                "warning_min": { label: "Min (warning)", type: "int", simple: true, warning: true },
                "warning_max": { label: "Max (warning)", type: "int", simple: true, warning: true },
                "type": { label: "Type", data: ["IN", "OUT"] },
                "allow_multiple": true
            },
            "port": {
                "itfIndex": { label: "Interface index", type: "int", simple: true },
                "oper_status": { label: "Status", data: [0, 1] },
                "allow_multiple": true
            },
            "server": {
                "one_minute_load": { check_type: "lt", type: "int", label: "Load (minuta)" },
                "five_minute_load": { check_type: "lt", type: "int", label: "Load (5 minut)" },
                "fifteen_minute_load": { check_type: "lt", type: "int", label: "Load (15 minut)" },
                "storage_used": { check_type: "lt", type: "int", label: "Disk space used" },
                "allow_multiple": false
            },
            "cmts_card": {
                "name": { label: "Name", type: "string" },
                "temperature": { label: "Temperature", check_type: "lt", type: "int" },
                "cpu": { label: "Cpu", check_type: "lt", type: "int" },
                "allow_multiple": true
            },
            "cmts_snr": {
                "warning": { label: "Warning", type: "int", warning: true },
                "critical": { label: "Critical", type: "int", critical: true },
                "allow_multiple": false
            },
            "ups": {
                "voltage": { label: "Voltage", check_type: "gt", type: "int" },
                "temperature": { label: "Temperature", check_type: "lt", type: "int" },
                "allow_multiple": false
            },
            "switch_heat": {
                "warning": { label: "Warning", type: "int", warning: true },
                "critical": { label: "Critical", type: "int", critical: true },
                "allow_multiple": false
            },
            "sensor": {
                "warning": { label: "Warning", type: "int", warning: true },
                "critical": { label: "Critical", type: "int", critical: true },
                "input": { label: "Input", data: [
                    "LAN_CONTROLLER_IN4",
                    "LAN_CONTROLLER_IN6",
                    "LAN_CONTROLLER_V2_IN4",
                    "LAN_CONTROLLER_V2_IN6",
                    "LB487"
                ] },
                "id": { label: "ID (only LB487)", type: "int" },
                "name": { label: "Name (only LB487)", type: "string" },
                "allow_multiple": true
            },
            "ignored_types": {
                "ignored_type": { label: "Typ", type: "string" },
                "allow_multiple": true
            }
        }
    }

    return obj;
});
