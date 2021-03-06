%setdefault('debug', True)
%setdefault('in_sidebar', False)

<!-- Dashboard actions bar -->
%if not in_sidebar:
<nav id="actionbar-menu" class="navbar navbar-default" >
   <ul class="nav navbar-nav navbar-left">
%end
      <li class="{{'dropdown' if in_sidebar else 'dropup'}}" data-toggle="tooltip" data-placement="right" title="{{_('Add a new widget')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-plug"></span>
            <span class="hidden-sm hidden-xs">{{_('Add a new widget')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Widgets menu')}}">
            %for widget in webui.get_widgets_for('dashboard'):
            <li>
               <a href="#"
                  class="dashboard-widget"
                  data-widget-title="
                      <button href='#' role='button'
                          data-action='add-widget'
                          data-widget-id='{{widget['id']}}'
                          data-widget-name='{{widget['name']}}'
                          data-widget-template='{{widget['template']}}'
                          data-widget-uri='{{widget['base_uri']}}'
                          class='btn btn-sm btn-success'>
                          <span class='fa fa-plus'></span>
                          {{_('Add this widget to your dashboard')}}
                      </button>"
                  data-widget-description='{{!widget["description"]}} <hr/> <div class="center-block"><img class="text-center" src="{{widget["picture"]}}"/></div>'
                  >
                  <span class="fa fa-{{widget['icon']}}"></span>
                  {{widget['name']}}
               </a>
            </li>
            %end
         </ul>
      </li>

%if debug:
      <li class="{{'dropdown' if in_sidebar else 'dropup'}}" data-toggle="tooltip" data-placement="right" title="{{_('External widgets')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-bug"></span>
            <span class="hidden-sm hidden-xs">{{_('External widgets')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu">
            %for widget in webui.get_widgets_for('external'):
            <li>
               <a href="/external/widget/{{widget['id']}}?page&widget_id={{widget['id']}}">
                  <span class="fa fa-fw fa-{{widget['icon']}}"></span>
                  {{widget['name']}} <em>(id: {{widget['id']}})</em>
               </a>
            </li>
            %end
         </ul>
      </li>
      %debug_host = datamgr.get_host({'name': 'webui'})
      %if debug_host:
      <li class="{{'dropdown' if in_sidebar else 'dropup'}}" data-toggle="tooltip" data-placement="right" title="{{_('Hosts widgets')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-bug"></span>
            <span class="hidden-sm hidden-xs">{{_('Hosts widgets')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu">
            %for widget in webui.get_widgets_for('host'):
            <li>
               <a href="/external/host/{{debug_host.id}}/{{widget['id']}}?page">
                  <span class="fa fa-fw fa-{{widget['icon']}}"></span>
                  {{widget['name']}} <em>(id: {{widget['id']}})</em>
               </a>
            </li>
            %end
         </ul>
      </li>
      %end
      <li class="{{'dropdown' if in_sidebar else 'dropup'}}" data-toggle="tooltip" data-placement="right" title="{{_('External tables')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-bug"></span>
            <span class="hidden-sm hidden-xs">{{_('External tables')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu">
            %for table in webui.get_tables_for('external'):
            <li>
               <a href="/external/table/{{table['id']}}?page&table_id={{table['id']}}">
                  <span class="fa fa-fw fa-{{table['icon']}}"></span>
                  {{table['name']}} <em>(id: {{widget['id']}})</em>
               </a>
            </li>
            %end
         </ul>
      </li>
%end

%if not in_sidebar:
   </ul>
</nav>
%end