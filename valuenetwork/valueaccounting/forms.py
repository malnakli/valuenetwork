import sys
import datetime
from decimal import *
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from valuenetwork.valueaccounting.models import *

from valuenetwork.valueaccounting.widgets import DurationWidget, DecimalDurationWidget


class FacetedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ": ".join([obj.name, obj.facet_values_list()])


class AgentModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

        
class WorkModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
        
class ResourceModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        label = obj.identifier
        if obj.current_location:
            loc = obj.current_location.name
            label = " ".join([obj.identifier, "at", loc])
        return label


class AgentForm(forms.Form):
    nick = forms.CharField(label="ID", widget=forms.TextInput(attrs={'class': 'required-field',}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    agent_type = forms.ModelChoiceField(
        queryset=AgentType.objects.all(),
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))



class AgentCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required-field input-xlarge',}))   
    nick = forms.CharField(label="ID", widget=forms.TextInput(attrs={'class': 'required-field',}))   
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    agent_type = forms.ModelChoiceField(
        queryset=AgentType.objects.all(),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))

    class Meta:
        model = EconomicAgent
        fields = ('name', 'nick', 'agent_type', 'description', 'url', 'address', 'email')


#todo: queryset methods cd be cached
class AgentSelectionForm(forms.Form):
    selected_agent = AgentModelChoiceField(
        queryset=EconomicAgent.objects.individuals_without_user(), 
        label="Select an existing Agent",
        required=False)

        
#changed to create context_agents
class ProjectForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = EconomicAgent
        fields = ('name', 'description')


class LocationForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Location
        fields = ('address', 'name', 'description', 'latitude', 'longitude')


class SelectResourceForm(forms.Form):
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Add quantity to selected resource",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    def __init__(self, resource_type=None, *args, **kwargs):
        super(SelectResourceForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if resource_type:
            self.fields["resource"].queryset = EconomicResource.goods.filter(resource_type=resource_type)

            
class SelectOrCreateResourceForm(forms.ModelForm):
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Add to selected resource or create new resource below",
        required=False,
        widget=forms.Select(attrs={'class': 'input-xlarge chzn-select',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value'), 
        label=_("Unit"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'input-medium',}))
    identifier = forms.CharField(
        required=False, 
        label="Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        required=False,
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium chzn-select',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    photo_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    notes = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    
    class Meta:
        model = EconomicResource
        fields = ('quantity', 'unit_of_quantity', 'identifier', 'current_location', 'url', 'photo_url', 'notes')
        
    def __init__(self, resource_type=None, *args, **kwargs):
        super(SelectOrCreateResourceForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if resource_type:
            self.fields["resource"].queryset = EconomicResource.goods.filter(resource_type=resource_type)


class EconomicResourceForm(forms.ModelForm):
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    photo_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    class Meta:
        model = EconomicResource
        exclude = ('resource_type', 'owner', 'author', 'custodian', 'photo',  'quality', 'independent_demand', 'order_item', 'stage', 'state')

        
class CreateEconomicResourceForm(forms.ModelForm):
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    photo_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    class Meta:
        model = EconomicResource
        exclude = ('resource_type', 'owner', 'author', 'custodian', 'quality', 'independent_demand', 'order_item', 'stage', 'state')


class ResourceQuantityForm(forms.Form):
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    
class AddOrderItemForm(forms.Form):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector chzn-select input-xlarge'}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    def __init__(self, resource_types, *args, **kwargs):
        super(AddOrderItemForm, self).__init__(*args, **kwargs)
        self.fields["resource_type"].queryset = resource_types
        

class ResourceRoleAgentForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    role = forms.ModelChoiceField(
        queryset=AgentResourceRoleType.objects.all(), 
        required=False)
    agent = AgentModelChoiceField(
        queryset=EconomicAgent.objects.resource_role_agents(), 
        required=False)
    is_contact = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())

    class Meta:
        model = AgentResourceRole
        fields = ('id', 'role', 'agent', 'is_contact')

class FailedOutputForm(forms.ModelForm):
    quantity = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class': 'failed-quantity input-small',}))
    description = forms.CharField(
        label="Why failed",
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = EconomicEvent
        fields = ('quantity', 'description')

class DemandSelectionForm(forms.Form):
    demand = forms.ModelChoiceField(
        queryset=Order.objects.exclude(order_type="holder"), 
        label="For customer or R&D order (optional)",
        required=False)


class OrderForm(forms.ModelForm):
    due_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-small',}))

    class Meta:
        model = Order
        exclude = ('order_date', 'order_type')

        
class ResourceTypeListForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xxlarge', }))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'description input-xxlarge',}))

    class Meta:
        model = ResourceTypeList

        
class ResourceTypeListElementForm(forms.ModelForm):
    resource_type_id = forms.IntegerField(widget=forms.HiddenInput)
    resource_type_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'input-xxlarge' }))
    #default_quantity = forms.DecimalField(required=False,
    #    widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity input-small'}))
    added = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'added',}))
    
    class Meta:
        model = ResourceTypeListElement
        exclude = ('resource_type_list', 'resource_type', 'default_quantity')
    
    
class RandOrderForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(),
        label="Receiver (optional)", 
        required=False)
    provider = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(), 
        label="Provider (optional)", 
        required=False)
    create_order = forms.BooleanField(
        label="R&D Order without receiver",
        required=False, 
        widget=forms.CheckboxInput())

    class Meta:
        model = Order
        fields = ('receiver', 'provider')
        
        
class OrderChangeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': '',}))
    receiver = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(),
        label="Receiver (optional)", 
        required=False)
    provider = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(), 
        label="Provider (optional)", 
        required=False)
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'description',}))

    class Meta:
        model = Order
        fields = ('name', 'receiver', 'provider', 'due_date', 'description')
        

class ProcessForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(),
        empty_label=None)
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))

    class Meta:
        model = Process
        fields = ('name', 'context_agent', 'process_pattern', 'start_date', 'end_date', 'notes' )

    def __init__(self, *args, **kwargs):
        super(ProcessForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.production_patterns()  
        
class WorkflowProcessForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge name',}))
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(),
        empty_label=None)
    process_type = forms.ModelChoiceField(
        required=False,
        queryset=ProcessType.objects.none(),
        label=_("Select an existing Process Type..."),
        #empty_label=None,
        widget=forms.Select(attrs={'class': 'process-type process-info'}))
    new_process_type_name = forms.CharField(
        required=False,
        label=_("...or create a new Process Type named:"),
        widget=forms.TextInput(attrs={'class': 'new-pt-name process-info input-xlarge',}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    
    class Meta:
        model = Process
        fields = ('name', 'context_agent', 'process_pattern', 'process_type', 'start_date', 'end_date', 'notes' )
        
    def __init__(self, order_item, next_date=None, *args, **kwargs):
        super(WorkflowProcessForm, self).__init__(*args, **kwargs)
        if next_date:
            self.fields["start_date"] = next_date
            self.fields["end_date"] = next_date
        self.fields["process_pattern"].queryset = ProcessPattern.objects.recipe_patterns() 
        #import pdb; pdb.set_trace()
        self.fields["process_type"].queryset = order_item.available_workflow_process_types()

        
class ScheduleProcessForm(forms.ModelForm):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))

    class Meta:
        model = Process
        fields = ('start_date', 'end_date', 'notes' )
        
        
class PlanProcessForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    
    class Meta:
        model = Process
        fields = ('name', 'start_date', 'end_date')


class AddProcessFromResourceForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(),
        required=False,
        empty_label=None)
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))

    class Meta:
        model = Process
        fields = ('name', 'context_agent', 'process_pattern', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super(AddProcessFromResourceForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.production_patterns()


class ProcessInputForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        widget=forms.Select(
            attrs={'class': 'resource-type-selector chzn-select input-xlarge'}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value'), 
        label=_("Unit"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        super(ProcessInputForm, self).__init__(*args, **kwargs)
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.input_resource_types()
                
#new
class UnplannedWorkEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Type of work done",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Work done by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))   
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value'), 
        label=_("Unit"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
   
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type', 'from_agent', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(UnplannedWorkEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.work_resource_types()]
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()


class ProcessConsumableForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value'), 
        label=_("Unit"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        super(ProcessConsumableForm, self).__init__(*args, **kwargs)
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.consumable_resource_types()


class ProcessUsableForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value'), 
        label=_("Unit"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        super(ProcessUsableForm, self).__init__(*args, **kwargs)
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.usable_resource_types()


#used in labnotes, create, copy and change_process, and create and change_rand
class ProcessOutputForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity  input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value').exclude(unit_type='time'), 
        empty_label=None,
        label=_("Unit"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        super(ProcessOutputForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.output_resource_types()


class UnplannedOutputForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    identifier = forms.CharField(
        required=False, 
        label="Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '1.0', 'class': 'quantity  input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value').exclude(unit_type='time'), 
        empty_label=None,
        label=_("Unit"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    url = forms.URLField(
        required=False, 
        label="URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    photo_url = forms.URLField(
        required=False, 
        label="Photo URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    notes = forms.CharField(
        required=False,
        label="Notes", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
        
    class Meta:
        model = EconomicEvent
        fields = ('resource_type', 'quantity', 'unit_of_quantity',)

    def __init__(self, pattern=None, *args, **kwargs):
        super(UnplannedOutputForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.output_resource_types()


class UnorderedReceiptForm(forms.ModelForm):
    event_date = forms.DateField(
        required=True, 
        label="Received on",
        widget=forms.TextInput(attrs={'class': 'input-small date-entry', }))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Supplier",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        help_text="If you don't see the resource type you want, please contact an admin.",
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    value = forms.DecimalField(
        help_text="Total value for all received, not value for each.",
        widget=forms.TextInput(attrs={'class': 'value input-small',}))
    unit_of_value = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.filter(unit_type='value'))
    quantity = forms.DecimalField(required=True,
        label="Quantity",
        widget=forms.TextInput(attrs={'value': '1', 'class': 'quantity  input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value').exclude(unit_type='time'), 
        empty_label=None,
        label=_("Unit"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False,
        label="Event Description", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    identifier = forms.CharField(
        required=False, 
        label="<b>Create the resource:</b><br><br>Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    url = forms.URLField(
        required=False, 
        label="URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    photo_url = forms.URLField(
        required=False, 
        label="Photo URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        required=False,
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    notes = forms.CharField(
        required=False,
        label="Resource Notes", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    access_rules = forms.CharField(
        required=False,
        label="Resource Access Rules", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
        
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'resource_type', 'value', 'unit_of_value', 'quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(UnorderedReceiptForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.receipt_resource_types()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_suppliers()            

            
class SelectResourceOfTypeForm(forms.Form):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        help_text="If you don't see the resource type you want, please contact an admin.",
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource resourceType chzn-select input-xlarge'}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.none(), 
        label="Add quantity to selected resource",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'resource input-xxlarge chzn-select',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    value = forms.DecimalField(
        label="Total value (not per unit)",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    unit_of_value = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.filter(unit_type='value'))
    description = forms.CharField(
        required=False,
        label="Event Description", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    
    def __init__(self, pattern=None, posting=False, *args, **kwargs):
        super(SelectResourceOfTypeForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            rts = pattern.receipt_resource_types_with_resources()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
            
class SelectContrResourceOfTypeForm(forms.Form):
    event_date = forms.DateField(
        required=True, 
        label="Received on",
        widget=forms.TextInput(attrs={'class': 'input-small date-entry', }))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Resource contributed by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        help_text="If you don't see the resource type you want, please contact an admin.",
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource resourceType chzn-select input-xlarge'}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.none(), 
        label="Add quantity to selected resource",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'resource input-xxlarge chzn-select',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    value = forms.DecimalField(
        label="Total value (not per unit)",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    unit_of_value = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.filter(unit_type='value'))
    description = forms.CharField(
        required=False,
        label="Event Description", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    
    def __init__(self, pattern=None, posting=False, *args, **kwargs):
        super(SelectContrResourceOfTypeForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            rts = pattern.matl_contr_resource_types_with_resources()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
                                

class TodoForm(forms.ModelForm):
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.individuals(),
        label="Assigned to",  
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        label="Type of work", 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'todo-description input-xlarge',}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))

    class Meta:
        model = Commitment
        fields = ('from_agent', 'context_agent', 'resource_type', 'due_date', 'description', 'url')

    def __init__(self, pattern=None, *args, **kwargs):
        super(TodoForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.todo_resource_types()]


#used in labnotes
class OldProcessCitationForm(forms.Form):
    #todo: this could now become a ModelChoiceField
    resource_type = forms.ChoiceField( 
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    def __init__(self, pattern=None, *args, **kwargs):
        super(ProcessCitationForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [('', '----------')] + [(rt.id, rt) for rt in pattern.citables_with_resources()]
        else:
            self.fields["resource_type"].choices = [('', '----------')] + [(rt.id, rt) for rt in EconomicResourceType.objects.all()]


class ProcessCitationForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(ProcessCitationForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.citable_resource_types()


#used in change_process        
class ProcessCitationCommitmentForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        widget=forms.Select(attrs={'class': 'input-xlarge'}))
    quantity = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('resource_type', 'description', 'quantity')

    def __init__(self, pattern=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(ProcessCitationCommitmentForm, self).__init__(*args, **kwargs)
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.citables_with_resources()

#this can go away when log simple goes away
class SelectCitationResourceForm(forms.Form):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        widget=forms.Select(attrs={'class': 'input-xxlarge', 'onchange': 'getResources();'}))
    resource = forms.ChoiceField(widget=forms.Select(attrs={'class': 'input-xlarge'})) 

    def __init__(self, pattern, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(SelectCitationResourceForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.citables_with_resources()

class UnplannedCiteEventForm(forms.Form):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        widget=forms.Select(attrs={'class': 'input-xxlarge res-ajax resourceType'}))
    resource = forms.ChoiceField(widget=forms.Select(attrs={'class': 'input-xlarge'})) 

    def __init__(self, pattern, load_resources=False, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(UnplannedCiteEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.citables_with_resources()
            if load_resources:
                resources = EconomicResource.objects.all()
                self.fields["resource"].choices = [('', '----------')] + [(r.id, r) for r in resources]

#todo: test this
class UnplannedInputEventForm(forms.Form):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        widget=forms.Select(attrs={'class': 'input-xxlarge resourceType resource-type-selector res-ajax'}))
    resource = forms.ChoiceField(widget=forms.Select(attrs={'class': 'input-xlarge'})) 
    quantity = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label = _("Unit"),
        queryset=Unit.objects.exclude(unit_type='value'),  
        widget=forms.Select())

    def __init__(self, pattern, load_resources=False, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(UnplannedInputEventForm, self).__init__(*args, **kwargs)
        if pattern:
            #import pdb; pdb.set_trace()
            self.pattern = pattern
            prefix = kwargs["prefix"]
            if prefix == "unplannedusable":
                self.fields["resource_type"].queryset = pattern.usables_with_resources()
            else:
                self.fields["resource_type"].queryset = pattern.consumables_with_resources()
            if load_resources:
                resources = EconomicResource.objects.all()
                self.fields["resource"].choices = [('', '----------')] + [(r.id, r) for r in resources]

'''
class CashEventAgentForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Type of cash",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Cash contributed by",  
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))    
   
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type','quantity', 'description', 'from_agent')

    def __init__(self, agent=None, date=None, pattern=None, context_agent=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(CashEventAgentForm, self).__init__(*args, **kwargs)
        if date:
            self.event_date = date
        if agent:
            self.from_agent = agent
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.work_resource_types()]
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()
''' 

class CommitmentForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(
        label="Estimated quantity (optional)",
        required=False, 
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('start_date', 'quantity', 'unit_of_quantity', 'description')


class ChangeCommitmentForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('due_date', 'quantity', 'description')


class ChangeWorkCommitmentForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = Commitment
        fields = ('due_date', 'quantity', 'unit_of_quantity', 'description')



class WorkbookForm(forms.ModelForm):
    work_done = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())
    process_done = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hours, minutes")
	
    class Meta:
        model = EconomicEvent
        fields = ('quantity', 'description')


class PastWorkForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    work_done = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())
    process_done = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput())
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hours, minutes")
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'event_date', 'quantity', 'description')


class OldUnplannedWorkEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Type of work done",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Work done by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))   
    quantity = forms.DecimalField(required=True,
        widget=DecimalDurationWidget,
        label="Time spent",
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
   
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type', 'from_agent', 'quantity', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(UnplannedWorkEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.work_resource_types()]
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()


class WorkEventAgentForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Type of work done",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(required=True,
        widget=DecimalDurationWidget,
        label="Time spent",
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Work done by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))    
   
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type','quantity', 'description', 'from_agent')

    def __init__(self, pattern, context_agent=None, *args, **kwargs):
        super(WorkEventAgentForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.work_resource_types()]
        #import pdb; pdb.set_trace()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()


class WorkCommitmentForm(forms.ModelForm):
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Type of work",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select resourceType resource-type-selector'})) 
    quantity = forms.DecimalField(required=True,
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
   
    class Meta:
        model = Commitment
        fields = ('resource_type','quantity', 'unit_of_quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(WorkCommitmentForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.work_resource_types()


class ProcessWorkForm(forms.ModelForm):
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Type of work",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(required=True,
        widget=DecimalDurationWidget,
        label="Estimated time",
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
   
    class Meta:
        model = Commitment
        fields = ('resource_type','quantity', 'description')

    def __init__(self, pattern=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(ProcessWorkForm, self).__init__(*args, **kwargs)
        #if pattern:
        #    self.pattern = pattern
        #    self.fields["resource_type"].queryset = pattern.work_resource_types()
        use_pattern = True
        if self.instance:
            if self.instance.id:
                use_pattern = False
                ct = Commitment.objects.get(id=self.instance.id)
                rt = ct.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.work_resource_types()



class WorkEventChangeForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'event_date', 'quantity', 'description')


class WorkEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'quantity', 'description')


class TimeEventForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hours, minutes")
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'event_date', 'quantity', 'description')


class InputEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'quantity', 'description')

    def __init__(self, qty_help=None, *args, **kwargs):
        super(InputEventForm, self).__init__(*args, **kwargs)
        if qty_help:
            self.fields["quantity"].help_text = qty_help


class WorkContributionChangeForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        label="Type of work", 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        label = "Time spent",
        help_text="hours, minutes")
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'event_date', 'resource_type', 'context_agent', 'quantity', 'url', 'description')


class EventChangeDateForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'event_date')

class EventChangeQuantityForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    quantity = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
	
    class Meta:
        model = EconomicEvent
        fields = ('id', 'quantity')

class PaymentEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Payment made to",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Payment made by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        label="Payment amount",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Cash resource type payment from",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource chzn-select'}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Cash resource account or earmark to decrease",
        required=False,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',})) 
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'to_agent', 'from_agent', 'quantity', 'resource_type', 'resource', 'description')

    def __init__(self, pattern=None, context_agent=None, posting=False, *args, **kwargs):
        super(PaymentEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            rts = pattern.payment_resource_types()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    if self.instance.id:
                        rt = self.instance.resource_type
                        if rt:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rt)
                        else:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
                    else:
                        self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
        if context_agent:
            self.context_agent = context_agent
            self.fields["to_agent"].queryset = context_agent.all_suppliers()
            self.fields["from_agent"].queryset = context_agent.all_ancestors_and_members()

class CashReceiptForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Payment received by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Payment made by",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        label="Receipt amount",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Cash resource type received into",
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'resource-type-for-resource resourceType chzn-select'})) 
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Cash resource account or earmark to increase",
        required=False,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))    
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'to_agent', 'quantity', 'resource_type', 'resource', 'description')

    def __init__(self, pattern=None, context_agent=None, posting=False, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(CashReceiptForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            rts = pattern.cash_receipt_resource_types()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    if self.instance.id:
                        rt = self.instance.resource_type
                        if rt:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rt)
                        else:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
                    else:
                        self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
        if context_agent:
            self.context_agent = context_agent
            self.fields["to_agent"].queryset = context_agent.all_ancestors()
            self.fields["from_agent"].choices = [('', '----------')] + [(ca.id, ca.nick) for ca in context_agent.all_customers()]
            

class CashReceiptResourceForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Payment received by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Payment made by",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        label="Receipt amount",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Cash resource type received into",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    identifier = forms.CharField(
        required=False, 
        label="<b>Create the resource:</b><br><br>Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        required=False,
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    notes = forms.CharField(
        required=False,
        label="Resource Notes", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'to_agent', 'quantity', 'resource_type', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(CashReceiptResourceForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.cash_receipt_resource_types()
        if context_agent:
            self.context_agent = context_agent
            self.fields["to_agent"].queryset = context_agent.all_ancestors()
            self.fields["from_agent"].choices = [('', '----------')] + [(ca.id, ca.nick) for ca in context_agent.all_customers()]
            

class DistributionEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Distributed to",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        label="Distribution amount",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="From cash resource type",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource chzn-select'}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Cash resource account or earmark to decrease",
        required=False,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'to_agent', 'quantity', 'resource_type', 'resource', 'description')

    def __init__(self, pattern=None, posting=False, *args, **kwargs):
        super(DistributionEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            rts = pattern.distribution_resource_types()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    if self.instance.id:
                        rt = self.instance.resource_type
                        if rt:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rt)
                        else:
                            self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
                    else:
                        self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])

class ShipmentForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Project",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    quantity = forms.DecimalField(
        label="Quantity shipped",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Resource shipped",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))
    value = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'value input-small',}))
    unit_of_value = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.filter(unit_type='value'))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'quantity', 'resource', 'value', 'unit_of_value', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(ShipmentForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource"].queryset = pattern.shipment_resources()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_ancestors()

class ExpenseEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Type of expense",
        empty_label=None,
        help_text="If you don't see the resource type you want, please contact an admin.",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    unit_of_value = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.filter(unit_type='value'))
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Supplier",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    value = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'value input-small',}))
    resource = ResourceModelChoiceField(
        required=False,
        queryset=EconomicResource.objects.all(), 
        label="Resource to reference",
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type', 'value', 'unit_of_value', 'from_agent', 'resource', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(ExpenseEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            #import pdb; pdb.set_trace()
            self.fields["resource_type"].queryset = pattern.expense_resource_types()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_suppliers()

class CashContributionEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    value = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'value input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Cash resource type",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource chzn-select'}))
    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Cash resource account or earmark to increase",
        required=False,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))  
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Contributor",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))


    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'value', 'resource_type', 'resource', 'description', 'is_contribution')

    def __init__(self, pattern=None, context_agent=None, posting=False, *args, **kwargs):
        super(CashContributionEventForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            rts = pattern.cash_contr_resource_types()
            self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()          

class CashContributionResourceEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    value = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'value input-small',}))
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(),
        label="Cash resource type",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Contributor",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    identifier = forms.CharField(
        required=False, 
        label="<b>Create the resource:</b><br><br>Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        required=False,
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    notes = forms.CharField(
        required=False,
        label="Resource Notes", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'value', 'resource_type', 'description', 'is_contribution')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(CashContributionResourceEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            #import pdb; pdb.set_trace()
            self.fields["resource_type"].queryset = pattern.cash_contr_resource_types()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.all_members()
            
class MaterialContributionEventForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Resource contributed by",  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        help_text="If you don't see the resource type you want, please contact an admin.",
        widget=forms.Select(
            attrs={'class': 'resource-type-selector resourceType chzn-select input-xlarge'}))
    quantity = forms.DecimalField(required=True,
        label="Quantity",
        widget=forms.TextInput(attrs={'value': '1', 'class': 'quantity  input-small'}))
    unit_of_quantity = forms.ModelChoiceField(
        queryset=Unit.objects.exclude(unit_type='value').exclude(unit_type='time'), 
        empty_label=None,
        label=_("Unit"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    value = forms.DecimalField(required=False,
        label="Approximate Value",
        widget=forms.TextInput(attrs={'value': '0', 'class': 'quantity  input-small'}))
    unit_of_value = forms.ModelChoiceField(required=False,
        queryset=Unit.objects.filter(unit_type='value'),
        label=_("Unit of Value"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    description = forms.CharField(
        required=False,
        label="Event Description", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    identifier = forms.CharField(
        required=False, 
        label="<b>Create the resource:</b><br><br>Identifier",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    url = forms.URLField(
        required=False, 
        label="URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    photo_url = forms.URLField(
        required=False, 
        label="Photo URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        required=False,
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium',}))
    notes = forms.CharField(
        required=False,
        label="Resource Notes", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    access_rules = forms.CharField(
        required=False,
        label="Resource Access Rules", 
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'from_agent', 'quantity', 'resource_type', 'unit_of_quantity', 'value', 'unit_of_value', 'description')

    def __init__(self, pattern=None, context_agent=None, *args, **kwargs):
        super(MaterialContributionEventForm, self).__init__(*args, **kwargs)
        if pattern:
            self.pattern = pattern
            self.fields["resource_type"].queryset = pattern.material_contr_resource_types() 
        if context_agent:
            self.context_agent = context_agent
            #self.fields["from_agent"].queryset = context_agent.all_members()


class WorkSelectionForm(forms.Form):
    type_of_work = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(WorkSelectionForm, self).__init__(*args, **kwargs)
        self.fields["type_of_work"].choices = [('', '----------')] + [(rt.id, rt.name) for rt in EconomicResourceType.objects.all()]


class ProjectSelectionForm(forms.Form):
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(),
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))


#used in view work, fixed to select context_agents
class ProjectSelectionFormOptional(forms.Form):
    context_agent = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ProjectSelectionFormOptional, self).__init__(*args, **kwargs)
        self.fields["context_agent"].choices = [('', '--All Projects--')] + [(proj.id, proj.name) for proj in EconomicAgent.objects.context_agents()]


class PatternSelectionForm(forms.Form):
    pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.all(),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))

    def __init__(self, queryset=None, *args, **kwargs):
        super(PatternSelectionForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields["pattern"].queryset = queryset

class UseCaseSelectionForm(forms.Form):
    use_case = forms.ModelChoiceField(
        queryset=UseCase.objects.all(),
        label=_("Select Use Case"),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))

class PatternProdSelectionForm(forms.Form):
    pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(),
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))

    def __init__(self, *args, **kwargs):
        super(PatternProdSelectionForm, self).__init__(*args, **kwargs)
        self.fields["pattern"].queryset = ProcessPattern.objects.production_patterns()   


class PatternFacetValueForm(forms.ModelForm):
    facet_value = forms.ModelChoiceField(
        queryset=FacetValue.objects.all(), 
        label="",
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))

    class Meta:
        model = PatternFacetValue
        fields = ('facet_value',)


class PatternAddFacetValueForm(forms.ModelForm):
    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.all(),
        label="",
        widget=forms.Select(attrs={'class': 'chzn-select input-medium'}))
    facet_value = forms.ModelChoiceField(
        queryset=FacetValue.objects.all(), 
        label="",
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))

    class Meta:
        model = PatternFacetValue
        fields = ('event_type', 'facet_value',)

    def __init__(self, qs=None, *args, **kwargs):
        super(PatternAddFacetValueForm, self).__init__(*args, **kwargs)
        if qs:
            self.fields["event_type"].queryset = qs


class ResourceTypeSelectionForm(forms.Form):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.none(), 
        label="Resource Type",
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))

    def __init__(self, qs=None, *args, **kwargs):
        super(ResourceTypeSelectionForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if qs:
            self.fields["resource_type"].queryset = qs    

        
class CasualTimeContributionForm(forms.ModelForm):
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    #project = forms.ModelChoiceField(
    #    queryset=Project.objects.all(), 
    #    empty_label=None, 
    #    widget=forms.Select(attrs={'class': 'chzn-select'}))
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'url',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hrs, mins")
	
    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type', 'context_agent', 'quantity', 'url', 'description')

    def __init__(self, *args, **kwargs):
        super(CasualTimeContributionForm, self).__init__(*args, **kwargs)
        pattern = None
        try:
            pattern = PatternUseCase.objects.get(use_case__identifier='non_prod').pattern
        except PatternUseCase.DoesNotExist:
            pass
        if pattern:
            self.fields["resource_type"].queryset = pattern.work_resource_types().order_by("name")

class HasAssociateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.inverse_label

                       
class HasAssociateForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    association_type = HasAssociateChoiceField(
        queryset=AgentAssociationType.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    is_associate = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(), 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'description',}))
    
    class Meta:
        model = AgentAssociation
        fields = ('id', 'association_type', 'is_associate', 'description', 'state')

    def __init__(self, *args, **kwargs):
        super(HasAssociateForm, self).__init__(*args, **kwargs)

            
class IsAssociateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.label

        
class IsAssociateForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    association_type = IsAssociateChoiceField(
        queryset=AgentAssociationType.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    has_associate = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.all(), 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'description',}))
    
    class Meta:
        model = AgentAssociation
        fields = ('id', 'association_type', 'has_associate', 'description', 'state')

    def __init__(self, *args, **kwargs):
        super(IsAssociateForm, self).__init__(*args, **kwargs)


class DateSelectionForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))


class DueDateAndNameForm(forms.Form):
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    order_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    

class StartDateAndNameForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    order_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    
    
class OrderDateAndNameForm(forms.Form):
    date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    start_date_or_due_date = forms.ChoiceField(
        choices=(("start", "start"),("due", "due")),
        widget=forms.Select(attrs={'class': 'input-small'}))
    order_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))

class DateAndNameForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    process_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-xlarge',}))


class ResourceTypeFacetValueForm(forms.Form):
    facet_id = forms.CharField(widget=forms.HiddenInput)
    value = forms.ChoiceField()


class OrderItemForm(forms.ModelForm):
    resource_type_id = forms.CharField(widget=forms.HiddenInput)
    quantity = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class': 'input-small',}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'url',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))

    def __init__(self, resource_type, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.resource_type = resource_type

    class Meta:
        model = Commitment
        fields = ('quantity', 'description')


class OrderItemOptionsForm(forms.Form):

    options = forms.ChoiceField()

    def __init__(self, feature, *args, **kwargs):
        super(OrderItemOptionsForm, self).__init__(*args, **kwargs)
        self.feature = feature
        self.fields["options"].choices = [(opt.id, opt.component.name) for opt in feature.options.all()]


class OptionsForm(forms.Form):

    options = forms.CharField(
        label=_("Options"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, feature, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)
        #todo: needs another way to limit choices
        #if feature.option_category:
        #    options = EconomicResourceType.objects.filter(category=feature.option_category)
        #else:
        #    options = EconomicResourceType.objects.all()
        options = EconomicResourceType.objects.all()
        self.fields["options"].choices = [(rt.id, rt.name) for rt in options]
        
        
def possible_parent_resource_types():
    rt_ids = [rt.id for rt in EconomicResourceType.objects.all() if rt.can_be_parent()]
    return EconomicResourceType.objects.filter(id__in=rt_ids)
    

class EconomicResourceTypeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'unique-name input-xlarge',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    substitutable = forms.BooleanField(
        required=False,
        help_text=_('Can any resource of this type be substituted for any other resource of this type?'),
        widget=forms.CheckboxInput()) 
    
    class Meta:
        model = EconomicResourceType
        exclude = ('created_by', 'changed_by',)

    def __init__(self, *args, **kwargs):
        super(EconomicResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["substitutable"].initial = settings.SUBSTITUTABLE_DEFAULT
        self.fields["parent"].queryset = possible_parent_resource_types()
        

class EconomicResourceTypeChangeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'existing-name input-xlarge',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all())
    
    class Meta:
        model = EconomicResourceType
        exclude = ('created_by', 'changed_by')
        
    def __init__(self, *args, **kwargs):
        super(EconomicResourceTypeChangeForm, self).__init__(*args, **kwargs)
        #todo pr: self.instance shd be excluded from parents
        self.fields["parent"].queryset = possible_parent_resource_types()


class EconomicResourceTypeAjaxForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'unique-name input-xlarge',}))
    unit = forms.ModelChoiceField(
        empty_label=None,
        queryset=Unit.objects.all())
    unit_of_use = forms.ModelChoiceField(
        required=False,
        queryset=Unit.objects.all())
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    photo_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    
    class Meta:
        model = EconomicResourceType
        exclude = ('parent', 'created_by', 'changed_by', 'photo')

class AgentResourceTypeForm(forms.ModelForm):
    lead_time = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'value': '0', 'class': 'numeric'}))
    value = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'numeric'}))

    def __init__(self, *args, **kwargs):
        super(AgentResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["agent"].choices = [
            (agt.id, agt.name) for agt in EconomicAgent.objects.all()
        ]


    class Meta:
        model = AgentResourceType
        exclude = ('resource_type', 'relationship', 'event_type', 'score')


class XbillProcessTypeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'name input-xlarge',}))
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        required=False, 
        #empty_label="---------",
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    quantity = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    estimated_duration = forms.IntegerField(required=False,
        widget=DurationWidget,
        help_text="days, hours, minutes")
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))

    class Meta:
        model = ProcessType
        exclude = ('parent','project')

    def __init__(self, *args, **kwargs):
        super(XbillProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.production_patterns()  

        
class RecipeProcessTypeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'name input-xlarge',}))
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        required=False, 
        #empty_label="---------",
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    #quantity = forms.DecimalField(
    #    max_digits=8, decimal_places=2,
    #    widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    estimated_duration = forms.IntegerField(required=False,
        widget=DurationWidget,
        help_text="days, hours, minutes")
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    
    class Meta:
        model = ProcessType
        exclude = ('parent','project', 'quantity')
        
    def __init__(self, *args, **kwargs):
        super(RecipeProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.recipe_patterns() 

        
class RecipeProcessTypeChangeForm(forms.ModelForm):
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        required=False, 
        #empty_label="---------",
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    estimated_duration = forms.IntegerField(required=False,
        widget=DurationWidget,
        help_text="days, hours, minutes")
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    
    class Meta:
        model = ProcessType
        exclude = ('parent',)
        
    def __init__(self, *args, **kwargs):
        super(RecipeProcessTypeChangeForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.recipe_patterns()
        if self.instance:
            pat = self.instance.process_pattern
            if pat:
                self.fields["process_pattern"].queryset = ProcessPattern.objects.filter(id=pat.id)
             

class ChangeProcessTypeForm(forms.ModelForm):
    estimated_duration = forms.IntegerField(required=False,
        widget=DurationWidget,
        help_text="days, hours, minutes")

    class Meta:
        model = ProcessType
        exclude = ('parent',)

class FeatureForm(forms.ModelForm):

    class Meta:
        model = Feature
        exclude = ('product', 'relationship', 'process_type')


class ProcessTypeResourceTypeForm(forms.ModelForm):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'resource-type-selector'}))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label=_("Unit"),
        queryset=Unit.objects.all(),  
        widget=forms.Select())

    class Meta:
        model = ProcessTypeResourceType
        exclude = ('process_type', 'relationship', 'event_type')


class ProcessTypeInputForm(forms.ModelForm):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(),  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label = _("Unit"),
        queryset=Unit.objects.all(),  
        widget=forms.Select())

    class Meta:
        model = ProcessTypeResourceType
        exclude = ('process_type', 'relationship', 'event_type', 'state', 'stage')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeInputForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                output_ids = [pt.id for pt in process_type.produced_resource_types()]
                self.fields["resource_type"].queryset = pattern.input_resource_types().exclude(id__in=output_ids)


class ProcessTypeConsumableForm(forms.ModelForm):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label = _("Unit"),
        queryset=Unit.objects.exclude(unit_type='value').exclude(unit_type='time'),  
        widget=forms.Select())

    class Meta:
        model = ProcessTypeResourceType
        exclude = ('process_type', 'relationship', 'event_type', 'state', 'stage')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeConsumableForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                output_ids = [pt.id for pt in process_type.produced_resource_types()]
                self.fields["resource_type"].queryset = pattern.consumable_resource_types().exclude(id__in=output_ids)
        if self.instance.id:
            pass
        else:
            if len(self.fields["resource_type"].queryset) > 0:
                self.fields["unit_of_quantity"].initial = self.fields["resource_type"].queryset[0].unit_for_use()


class ProcessTypeUsableForm(forms.ModelForm):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(),  
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label = _("Unit"),
        queryset=Unit.objects.exclude(unit_type='value'),  
        widget=forms.Select())

    class Meta:
        model = ProcessTypeResourceType
        exclude = ('process_type', 'relationship', 'event_type', 'state', 'stage')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeUsableForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                output_ids = [pt.id for pt in process_type.produced_resource_types()]
                self.fields["resource_type"].queryset = pattern.usable_resource_types().exclude(id__in=output_ids)
        if self.instance.id:
            pass
        else:
            if len(self.fields["resource_type"].queryset) > 0:
                self.fields["unit_of_quantity"].initial = self.fields["resource_type"].queryset[0].unit_for_use()

        
class ProcessTypeCitableForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = ProcessTypeResourceType
        fields = ('resource_type', 'description')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeCitableForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                output_ids = [pt.id for pt in process_type.produced_resource_types()]
                self.fields["resource_type"].queryset = pattern.citable_resource_types().exclude(id__in=output_ids)

                
class ProcessTypeCitableStreamRecipeForm(forms.ModelForm):
    resource_type = FacetedModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    description = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))

    class Meta:
        model = ProcessTypeResourceType
        fields = ('resource_type', 'description')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeCitableStreamRecipeForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.citable_resource_types()
              
                
class ProcessTypeWorkForm(forms.ModelForm):
    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(), 
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'resource-type-selector input-xlarge' }))
    quantity = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'quantity'}))
    unit_of_quantity = forms.ModelChoiceField(
        required = False,
        label=_("Unit"),
        queryset=Unit.objects.all(),  
        widget=forms.Select())

    class Meta:
        model = ProcessTypeResourceType
        exclude = ('process_type', 'relationship', 'event_type', 'state', 'stage')

    def __init__(self, process_type=None, *args, **kwargs):
        super(ProcessTypeWorkForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        use_pattern = True
        pattern = None
        if process_type:
            pattern = process_type.process_pattern
        if self.instance:
            if self.instance.id:
                use_pattern = False
                inst = ProcessTypeResourceType.objects.get(id=self.instance.id)
                rt = inst.resource_type
                self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=rt.id)
        if pattern:
            if use_pattern:
                self.pattern = pattern
                self.fields["resource_type"].queryset = pattern.work_resource_types()


class TimeForm(forms.Form):

    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(attrs={"cols": "80"}),
    )
    url = forms.CharField(
        label=_("URL"),
        max_length=96,
        required=False,
        widget=forms.TextInput(attrs={"size": "80"}),
    )

class EquationForm(forms.Form):

    equation = forms.CharField(
        label=_("Equation"),
        required=True,
        widget=forms.Textarea(attrs={"rows": "4", "cols": "60"}),
    )

    amount = forms.CharField(
        label=_("Amount to distribute"),
        required=False,
        widget=forms.TextInput(),
    )


    def clean_equation(self):
        equation = self.cleaned_data["equation"]
        safe_dict = {}
        safe_dict['hours'] = 1
        safe_dict['rate'] = 1
        safe_dict['importance'] = 1
        safe_dict['reputation'] = 1
        safe_dict['seniority'] = 1

        try:
            eval(equation, {"__builtins__":None}, safe_dict)
        except NameError:
            raise forms.ValidationError(sys.exc_info()[1])
        except SyntaxError:
            raise forms.ValidationError("Equation syntax error")
        except:
            raise forms.ValidationError(sys.exc_info()[0])

        return equation


class ExchangeForm(forms.ModelForm):
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        label=_("Pattern"),
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    start_date = forms.DateField(required=True, 
        label=_("Date"),
        widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    supplier = forms.ModelChoiceField(required=False,
        queryset=EconomicAgent.objects.none(),
        label="Supplier",  
        help_text="This is a supplier external to the network.  It is used as a default for individual events in this contribution.",
        widget=forms.Select(
            attrs={'class': 'chzn-select'})) 
    notes = forms.CharField(required=False, 
        label=_("Comments"),
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    url = forms.CharField(required=False, 
        label=_("Link to receipt(s)"),
        widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))

    class Meta:
        model = Exchange
        fields = ('process_pattern', 'context_agent', 'supplier', 'start_date', 'url', 'notes')

    def __init__(self, use_case, context_agent, *args, **kwargs):
        super(ExchangeForm, self).__init__(*args, **kwargs)
        self.fields["process_pattern"].queryset = ProcessPattern.objects.usecase_patterns(use_case) 
        if context_agent:
            self.fields["supplier"].queryset = context_agent.all_suppliers()
            
class SaleForm(forms.ModelForm):
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        label=_("Pattern"),
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(), 
        label=_("Project"),
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    start_date = forms.DateField(required=True, 
        label=_("Date"),
        widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    customer = forms.ModelChoiceField(required=False,
        queryset=EconomicAgent.objects.none(),
        label="Customer",
        widget=forms.Select(attrs={'class': 'chzn-select'})) 
    notes = forms.CharField(required=False, 
        label=_("Comments"),
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    
    class Meta:
        model = Exchange
        fields = ('process_pattern', 'context_agent', 'customer', 'start_date', 'notes')
        
    def __init__(self, context_agent=None, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(SaleForm, self).__init__(*args, **kwargs)
        use_case = UseCase.objects.get(identifier="sale")
        self.fields["process_pattern"].queryset = ProcessPattern.objects.usecase_patterns(use_case) 
        if context_agent:
            self.fields["customer"].queryset = context_agent.all_customers()
            
class DistributionForm(forms.ModelForm):
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.none(), 
        label=_("Pattern"),
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    start_date = forms.DateField(required=True, 
        label=_("Date"),
        widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    notes = forms.CharField(required=False, 
        label=_("Comments"),
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    
    class Meta:
        model = Exchange
        fields = ('process_pattern', 'start_date', 'notes')
        
    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(DistributionForm, self).__init__(*args, **kwargs)
        use_case = UseCase.objects.get(identifier="distribution")
        self.fields["process_pattern"].queryset = ProcessPattern.objects.usecase_patterns(use_case)
  
class DistributionValueEquationForm(forms.ModelForm):
    process_pattern = forms.ModelChoiceField(
        queryset=ProcessPattern.objects.all(), 
        label=_("Pattern"),
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 'pattern-selector'}))
    start_date = forms.DateField(required=True, 
        label=_("Date"),
        widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    value_equation = forms.ModelChoiceField(
        queryset=ValueEquation.objects.all(), 
        label=_("Value Equation"),
        empty_label=None, 
        widget=forms.Select(
            attrs={'class': 've-selector'}))
    notes = forms.CharField(required=False, 
        label=_("Comments"),
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    money_to_distribute = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={'value': '0.00', 'class': 'money'}))
    resource = forms.ModelChoiceField(
        queryset=EconomicResource.objects.all(), 
        label="Cash resource account",
        required=False,
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',})) 
    #todo: choose cash receipts
    
    class Meta:
        model = Exchange
        fields = ('process_pattern', 'start_date', 'notes')
        
    def __init__(self, context_agent=None, post=False, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(DistributionValueEquationForm, self).__init__(*args, **kwargs)
        if post == False:
            use_case = UseCase.objects.get(identifier="distribution")
            self.fields["process_pattern"].queryset = ProcessPattern.objects.usecase_patterns(use_case)
            if context_agent:
                self.fields["value_equation"].queryset = context_agent.value_equations
            if self.fields["process_pattern"].queryset.count > 0:
                resources = []
                pattern = self.fields["process_pattern"].queryset[0]
                rts = pattern.distribution_resource_types()
                if rts:
                    for rt in rts:
                        rss = rt.all_resources()
                        for res in rss:
                            resources.append(res)
                self.fields["resource"].choices = [('', '----------')] + [(res.id, res.identifier) for res in resources]
        #import pdb; pdb.set_trace()
                       
