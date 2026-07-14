'use client'

import { Input, Select } from '@sutra/ui'

interface UserDetailsStepProps {
  formData: {
    phone: string
    state: string
    city: string
    age_group: string
  }
  onChange: (field: string, value: string) => void
}

const INDIAN_STATES = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry'
]

const AGE_GROUPS = [
  '18-25',
  '26-35',
  '36-50',
  '51-65',
  '65+'
]

export default function UserDetailsStep({ formData, onChange }: UserDetailsStepProps) {
  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-content mb-2">
          Basic Details
        </h2>
        <p className="text-content-muted">
          Help us personalize your experience
        </p>
      </div>

      {/* Phone Number */}
      <div>
        <label className="block text-sm font-medium text-content mb-2">
          Phone Number <span className="text-content-subtle">(Optional)</span>
        </label>
        <Input
          type="tel"
          size="lg"
          value={formData.phone}
          onChange={(e) => onChange('phone', e.target.value)}
          placeholder="+91-9876543210"
          aria-label="Phone Number"
        />
      </div>

      {/* State */}
      <div>
        <label className="block text-sm font-medium text-content mb-2">
          State <span className="text-danger">*</span>
        </label>
        <Select
          size="lg"
          value={formData.state}
          onChange={(e) => onChange('state', e.target.value)}
          required
          aria-label="State"
          className={formData.state ? '' : 'text-content-subtle'}
        >
          <option value="">Select your state</option>
          {INDIAN_STATES.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </Select>
      </div>

      {/* City */}
      <div>
        <label className="block text-sm font-medium text-content mb-2">
          City <span className="text-content-subtle">(Optional)</span>
        </label>
        <Input
          type="text"
          size="lg"
          value={formData.city}
          onChange={(e) => onChange('city', e.target.value)}
          placeholder="Enter your city"
          aria-label="City"
        />
      </div>

      {/* Age Group */}
      <div>
        <label className="block text-sm font-medium text-content mb-2">
          Age Group <span className="text-danger">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {AGE_GROUPS.map((age) => (
            <button
              key={age}
              type="button"
              onClick={() => onChange('age_group', age)}
              className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                formData.age_group === age
                  ? 'border-accent bg-accent-subtle text-accent-subtle-content'
                  : 'border-border bg-surface text-content hover:border-accent'
              }`}
            >
              {age}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
