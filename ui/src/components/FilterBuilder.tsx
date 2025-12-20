import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';

interface FilterCriteria {
  service?: string;
  region?: string;
  tagKey?: string;
  tagValue?: string;
  minCost?: number;
  maxCost?: number;
  ageInDays?: number;
  state?: string;
}

interface FilterBuilderProps {
  onFilterChange: (filters: FilterCriteria) => void;
  onApply: () => void;
}

const SERVICES = [
  'ec2', 's3', 'rds', 'lambda', 'iam', 'dynamodb', 'cloudformation',
  'ecs', 'ecr', 'eks', 'sns', 'sqs', 'cloudwatch', 'apigateway',
  'apigatewayv2', 'elb', 'elbv2', 'route53', 'vpc', 'athena',
  'kinesis', 'glue', 'redshift', 'elasticache', 'kms', 'secretsmanager', 'guardduty'
];

const REGIONS = [
  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
  'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
  'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2',
  'ap-south-1', 'ca-central-1', 'sa-east-1'
];

const STATES = ['running', 'stopped', 'available', 'in-use', 'pending', 'terminated'];

export function FilterBuilder({ onFilterChange, onApply }: FilterBuilderProps) {
  const [filters, setFilters] = useState<FilterCriteria>({});
  const [savedFilters, setSavedFilters] = useState<FilterCriteria[]>([]);

  const updateFilter = (key: keyof FilterCriteria, value: any) => {
    const updated = { ...filters, [key]: value };
    setFilters(updated);
    onFilterChange(updated);
  };

  const clearFilters = () => {
    setFilters({});
    onFilterChange({});
  };

  const saveFilter = () => {
    setSavedFilters([...savedFilters, filters]);
    alert('Filter preset saved successfully!');
  };

  const loadFilter = (preset: FilterCriteria) => {
    setFilters(preset);
    onFilterChange(preset);
  };

  const activeFilterCount = Object.keys(filters).filter(
    key => filters[key as keyof FilterCriteria] !== undefined && filters[key as keyof FilterCriteria] !== ''
  ).length;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Advanced Filters</span>
          <span className="text-sm font-normal text-muted-foreground">
            {activeFilterCount} active filter{activeFilterCount !== 1 ? 's' : ''}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Service Selection */}
        <div className="space-y-2">
          <Label htmlFor="service">Service</Label>
          <Select
            value={filters.service || ''}
            onValueChange={(value) => updateFilter('service', value)}
          >
            <SelectTrigger id="service">
              <SelectValue placeholder="Select service" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Services</SelectItem>
              {SERVICES.map(service => (
                <SelectItem key={service} value={service}>
                  {service.toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Region Selection */}
        <div className="space-y-2">
          <Label htmlFor="region">Region</Label>
          <Select
            value={filters.region || ''}
            onValueChange={(value) => updateFilter('region', value)}
          >
            <SelectTrigger id="region">
              <SelectValue placeholder="Select region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Regions</SelectItem>
              {REGIONS.map(region => (
                <SelectItem key={region} value={region}>
                  {region}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tag Filters */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="tagKey">Tag Key</Label>
            <Input
              id="tagKey"
              placeholder="e.g., env"
              value={filters.tagKey || ''}
              onChange={(e) => updateFilter('tagKey', e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="tagValue">Tag Value</Label>
            <Input
              id="tagValue"
              placeholder="e.g., dev"
              value={filters.tagValue || ''}
              onChange={(e) => updateFilter('tagValue', e.target.value)}
            />
          </div>
        </div>

        {/* Cost Range */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="minCost">Min Cost ($)</Label>
            <Input
              id="minCost"
              type="number"
              placeholder="0"
              value={filters.minCost || ''}
              onChange={(e) => updateFilter('minCost', parseFloat(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="maxCost">Max Cost ($)</Label>
            <Input
              id="maxCost"
              type="number"
              placeholder="1000"
              value={filters.maxCost || ''}
              onChange={(e) => updateFilter('maxCost', parseFloat(e.target.value))}
            />
          </div>
        </div>

        {/* Age Filter */}
        <div className="space-y-2">
          <Label htmlFor="ageInDays">Age (days)</Label>
          <Input
            id="ageInDays"
            type="number"
            placeholder="e.g., 30 for resources older than 30 days"
            value={filters.ageInDays || ''}
            onChange={(e) => updateFilter('ageInDays', parseInt(e.target.value))}
          />
        </div>

        {/* State Filter */}
        <div className="space-y-2">
          <Label htmlFor="state">State</Label>
          <Select
            value={filters.state || ''}
            onValueChange={(value) => updateFilter('state', value)}
          >
            <SelectTrigger id="state">
              <SelectValue placeholder="Select state" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All States</SelectItem>
              {STATES.map(state => (
                <SelectItem key={state} value={state}>
                  {state.charAt(0).toUpperCase() + state.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4">
          <Button onClick={onApply} className="flex-1">
            Apply Filters
          </Button>
          <Button onClick={clearFilters} variant="outline" className="flex-1">
            Clear All
          </Button>
        </div>

        {/* Save/Load Filter Presets */}
        <div className="flex gap-2">
          <Button onClick={saveFilter} variant="secondary" className="flex-1">
            Save Preset
          </Button>
        </div>

        {/* Saved Presets */}
        {savedFilters.length > 0 && (
          <div className="space-y-2 pt-2 border-t">
            <Label>Saved Presets</Label>
            <div className="space-y-1">
              {savedFilters.map((preset, index) => (
                <Button
                  key={index}
                  onClick={() => loadFilter(preset)}
                  variant="ghost"
                  className="w-full justify-start text-sm"
                >
                  Preset {index + 1} ({Object.keys(preset).length} filters)
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Current Filter Summary */}
        {activeFilterCount > 0 && (
          <div className="pt-2 border-t">
            <Label className="text-xs text-muted-foreground">Active Filters:</Label>
            <div className="flex flex-wrap gap-1 mt-2">
              {Object.entries(filters).map(([key, value]) => {
                if (value === undefined || value === '') return null;
                return (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-md text-xs"
                  >
                    <span className="font-medium">{key}:</span>
                    <span>{String(value)}</span>
                    <button
                      onClick={() => updateFilter(key as keyof FilterCriteria, undefined)}
                      className="ml-1 hover:text-destructive"
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
