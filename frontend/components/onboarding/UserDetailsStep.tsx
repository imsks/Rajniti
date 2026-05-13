'use client'

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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Basic Details
        </h2>
        <p className="text-gray-600">
          Help us personalize your experience
        </p>
      </div>

      {/* Phone Number */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Phone Number <span className="text-gray-400">(Optional)</span>
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => onChange('phone', e.target.value)}
          placeholder="+91-9876543210"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
        />
      </div>

      {/* State */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          State <span className="text-red-500">*</span>
        </label>
        <select
          value={formData.state}
          onChange={(e) => onChange('state', e.target.value)}
          className={`w-full px-4 py-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
            formData.state ? 'text-gray-900' : 'text-gray-400'
          }`}
          required
        >
          <option value="" className="text-gray-400 bg-white">Select your state</option>
          {INDIAN_STATES.map((state) => (
            <option key={state} value={state} className="text-gray-900 bg-white">
              {state}
            </option>
          ))}
        </select>
      </div>

      {/* City */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          City <span className="text-gray-400">(Optional)</span>
        </label>
        <input
          type="text"
          value={formData.city}
          onChange={(e) => onChange('city', e.target.value)}
          placeholder="Enter your city"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
        />
      </div>

      {/* Age Group */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Age Group <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {AGE_GROUPS.map((age) => (
            <button
              key={age}
              type="button"
              onClick={() => onChange('age_group', age)}
              className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                formData.age_group === age
                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-orange-300'
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
