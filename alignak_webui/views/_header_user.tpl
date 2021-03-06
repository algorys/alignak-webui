%setdefault('debug', False)
%setdefault('edition_mode', False)

%if debug:
<li class="dropdown">
   <a href="#" class="dropdown-toggle" data-original-title="Debug" data-toggle="dropdown">
      <span class="fa fa-bug"></span>
      <span class="caret"></span>
   </a>
   <ul class="dropdown-menu">
      <li>
         <div class="panel panel-default">
            <div class="panel-body">
               <ul class="list-group">
                  <li class="list-group-item"><small>Current user: {{current_user}}</small></li>
                  <li class="list-group-item"><small>Target user: {{target_user}}</small></li>
               </ul>
               <div class="panel-footer">Total: {{datamgr.get_objects_count('user')}} users</div>
            </div>
         </div>
      </li>
   </ul>
</li>
%end

<!-- User info -->
<li class="dropdown user user-menu hidden-xs">
   <a href="#" class="dropdown-toggle" data-original-title="{{_('User menu')}}" data-toggle="dropdown">
      <span class="fa fa-user"></span>
      %if request.app.config.get('target_user', 'no') == 'yes':
      %if not target_user.is_anonymous() and current_user.get_username() != target_user.get_username():
      <span class="label label-warning" style="position:relative; left: 0px">{{target_user.get_username()}}</span>
      %end
      %end
      <span class="username hidden-sm hidden-xs hidden-md">{{current_user.name}}</span>
      <span class="caret"></span>
   </a>

   <ul class="dropdown-menu">
      %if request.app.config.get('target_user', 'no') == 'yes':
      <li class="user-header">
         %include("_select_target_user")
      </li>
      %end
      <li class="user-header">
         <div class="panel panel-info" id="user_info">
            <div class="panel-body panel-default">
               <!-- User image / name -->
               <p class="username">{{current_user.alias}}</p>
               <p class="usercategory">
                  <small>{{current_user.get_role(display=True)}}</small>
               </p>
               <img src="{{current_user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % current_user.name}}" title="{{_('Photo: %s') % current_user.name}}">
            </div>
            <div class="panel-footer">
               <div class="btn-group" role="group">
                  <a class="btn btn-default" href="#"
                     data-action="about-box" data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Display application information')}}">
                     <span class="fa fa-question"></span>
                  </a>
                  %if current_user.is_administrator():
                  <a class="btn btn-default" href="#"
                     data-action="edition-mode" data-state="{{'on' if edition_mode else 'off'}}" data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Enter edition mode')}}">
                     <span class="text-danger fa fa-edit"></span>
                  </a>

                  <a class="btn btn-default" href="/preferences/user"
                     data-action="user-preferences" data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Show all the stored user preferences')}}">
                     <span class="fa fa-pencil"></span>
                  </a>
                  %end
                  <a class="btn btn-default" href="/logout"
                     data-action="logout" data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Disconnect from the application')}}">
                     <span class="fa fa-sign-out"></span>
                  </a>
               </div>
            </div>
         </div>
      </li>
   </ul>
</li>
