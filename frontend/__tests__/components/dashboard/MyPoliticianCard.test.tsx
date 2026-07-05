import { fireEvent, render, screen } from '@testing-library/react'
import MyPoliticianCard from '@/components/MyPoliticianCard'
import { mockMp } from '@/__tests__/helpers/politicianFixtures'

describe('MyPoliticianCard', () => {
  it('shows placeholder with label and Add button', () => {
    const onAddClick = jest.fn()

    render(
      <MyPoliticianCard
        politician={null}
        slotType="MP"
        onAddClick={onAddClick}
      />,
    )

    expect(screen.getByText('Your MP')).toBeInTheDocument()
    expect(screen.getByText('Search above to add')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '+ Add' }))
    expect(onAddClick).toHaveBeenCalledTimes(1)
  })

  it('shows politician details when filled', () => {
    render(
      <MyPoliticianCard politician={mockMp} slotType="MP" onRemove={jest.fn()} />,
    )

    expect(screen.getByText('Narendra Modi')).toBeInTheDocument()
    expect(screen.getByText('MP of Varanasi')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'View more' })).toHaveAttribute(
      'href',
      '/politician/mp-1',
    )
  })

  it('calls onRemove when remove button is clicked', () => {
    const onRemove = jest.fn()

    render(
      <MyPoliticianCard politician={mockMp} slotType="MP" onRemove={onRemove} />,
    )

    fireEvent.click(
      screen.getByRole('button', { name: 'Remove from your politicians' }),
    )
    expect(onRemove).toHaveBeenCalledTimes(1)
  })
})
