%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/services")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_host import Host

<!-- services filtering and display -->
<div id="services">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_services"><i class="fa fa-bug"></i> Services as dictionaries</a>
            </h4>
         </div>
         <div id="collapse_services" class="panel-collapse collapse">
            <ul class="list-group">
               %for service in services:
                  <li class="list-group-item"><small>Service: {{service}} - {{service.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(services)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not services:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Host')}}</th>
               <th>{{_('Service')}}</th>
               <th>{{_('Business impact')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Last check output')}}</th>
            </tr></thead>

            <tbody>
               %for service in services:
               %lv_service = datamgr.get_livestate({'where': {'host': service.host.id, 'service': service.id}})
               %lv_service = lv_service[0]
               <tr id="#{{service.id}}">
                  <td title="{{service.alias}}">
                  %if lv_service:
                     %title = "%s - %s (%s)" % (lv_service.status, Helper.print_duration(lv_service.last_check, duration_only=True, x_elts=0), lv_service.output)
                     {{! lv_service.get_html_state(text=None, title=title)}}
                  %else:
                     {{! service.get_html_state(text=None, title=_('No livestate for this element'))}}
                  %end
                  </td>

                  <td>
                     <small>{{! service.host.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{! service.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_html_business_impact(service.business_impact)}}</small>
                  </td>

                  <td>
                     <small>{{! service.check_command.get_html_link()}}</small>
                  </td>

                  <td>
                  %if lv_service:
                     <small>{{! lv_service.output}}</small>
                  %end
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

%if layout:
 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
%end
