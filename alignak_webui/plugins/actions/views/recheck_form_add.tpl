%setdefault('read_only', False)
%setdefault('auto_post', False)

%# recheck attributes
%setdefault('action', 'add')
%setdefault('livestate_id', '-1')

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small><em>
      {{', '.join(element_name)}}
   </em></small>
</div>

<div class="modal-body">
   <form data-item="recheck" data-action="recheck" class="form-horizontal" method="post" action="/recheck/add" role="form">
      <div class="form-group" style="display: none">
         %for id in livestate_id:
         <input type="text" readonly id="livestate_id" name="livestate_id" value="{{id}}">
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}">
         %end
      </div>

      <div class="form-group">
         <div class="col-sm-12">
            <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
         </div>
      </div>

      <button type="submit" class="btn btn-success btn-lg btn-block"> <i class="fa fa-check"></i>{{_('Request recheck')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="recheck"]').submit();
   %end
});
</script>
