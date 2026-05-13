import { fireEvent, render, screen } from '@testing-library/react'
import UserDetailsStep from '@/components/onboarding/UserDetailsStep'
import UsernameStep from '@/components/onboarding/UsernameStep'

describe('onboarding field contrast styles', () => {
  it('applies high-contrast classes to basic detail inputs and state select', () => {
    const onChange = jest.fn()

    render(
      <UserDetailsStep
        formData={{ phone: '', state: '', city: '', age_group: '' }}
        onChange={onChange}
      />
    )

    const phoneInput = screen.getByPlaceholderText('+91-9876543210')
    const cityInput = screen.getByPlaceholderText('Enter your city')
    const stateSelect = screen.getByRole('combobox')

    expect(phoneInput).toHaveClass('bg-white', 'text-gray-900', 'placeholder:text-gray-500')
    expect(cityInput).toHaveClass('bg-white', 'text-gray-900', 'placeholder:text-gray-500')
    expect(stateSelect).toHaveClass('bg-white', 'text-gray-500')

    fireEvent.change(stateSelect, { target: { value: 'Delhi' } })
    expect(onChange).toHaveBeenCalledWith('state', 'Delhi')
  })

  it('applies high-contrast classes to username input', () => {
    render(
      <UsernameStep
        value=""
        onChange={jest.fn()}
        onValidation={jest.fn()}
      />
    )

    expect(screen.getByPlaceholderText('johndoe')).toHaveClass(
      'bg-white',
      'text-gray-900',
      'placeholder:text-gray-500'
    )
  })
})
