from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Milestone
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date cannot be before start date")
        return cleaned_data

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'start_date', 'due_date', 'duration', 'status', 'description', 'dependencies']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Limit dependencies to milestones within the same project
        # Exclude the current milestone if we're editing
        if self.project:
            milestone_queryset = Milestone.objects.filter(project=self.project)
            if self.instance.pk:
                milestone_queryset = milestone_queryset.exclude(pk=self.instance.pk)
            self.fields['dependencies'].queryset = milestone_queryset
            self.fields['dependencies'].label = "Depends on (milestones that must be completed first)"
            self.fields['dependencies'].widget = forms.CheckboxSelectMultiple()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        project = self.project

        if start_date and due_date:
            # Check if start date is before due date
            if start_date > due_date:
                raise ValidationError("Start date cannot be after due date")
            
            # Check if dates are within project timeframe
            if project:
                if start_date < project.start_date:
                    self.add_error('start_date', "Start date cannot be before project start date")
                if due_date > project.end_date:
                    self.add_error('due_date', "Due date cannot be after project end date")
            
            # Calculate and update duration
            from datetime import timedelta
            duration = (due_date - start_date).days + 1  # +1 to include both start and end dates
            cleaned_data['duration'] = duration
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If only due_date is provided, set start_date = due_date
        if instance.due_date and not instance.start_date:
            instance.start_date = instance.due_date
            instance.duration = 1
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
    
class ProjectShareForm(forms.Form):
    email = forms.EmailField(label="Collaborator's email")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email address was found.")
        return email