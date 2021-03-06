<!-- Hosts chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%if not hosts:
   <center>
      <h3>{{_('No hosts matching the filter...')}}</h3>
   </center>
%else:
   %hs = datamgr.get_livesynthesis()['hosts_synthesis']
   %if hs:
   <div class="well">
      <!-- Chart -->
      <div id="pc_hosts_{{widget_id}}">
         <canvas></canvas>
      </div>
   </div>
   %end
%end
<script>
   // Note: g_ prefixed variables are defined in the global alignak_layout.js file.
   $(document).ready(function() {
      var data=[], labels=[], colors=[], hover_colors=[];
      %for state in 'up', 'unreachable', 'down', 'acknowledged', 'in_downtime':
         labels.push(g_hosts_states["{{state.lower()}}"]['label']);
         data.push({{hs["nb_" + state]}});
         colors.push(g_hosts_states["{{state.lower()}}"]['color'])
         hover_colors.push(g_hoverBackgroundColor)
      %end
      var data = {
         labels: labels,
         datasets: [
            {
               data: data,
               backgroundColor: colors,
               hoverBackgroundColor: hover_colors
            }
         ]
      };
      var ctx = $("#pc_hosts_{{widget_id}} canvas");

      // Create chart
      var myBarChart = new Chart(ctx, {
         type: 'doughnut',
         data: data,
         options: {
            title: {
               display: true,
               text: '{{title}}'
            },
            legend: {
               display: true,
               position: 'bottom'
            }
         }
      });
   });
</script>