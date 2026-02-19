import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"

export default function Footer() {
    return (
        <footer className='bg-[#0F1F3D] py-10'>
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='flex flex-col sm:flex-row justify-between items-center gap-6'>
                    {/* Logo */}
                    <div className='flex items-center gap-2'>
                        <span className='font-serif text-2xl font-semibold text-white'>
                            Raj<span className='text-orange-500'>niti</span>
                        </span>
                    </div>

                    {/* Center Text */}
                    <div className='text-center'>
                        <Text variant='small' className='text-gray-400'>
                            Open source · Built for India · Community driven
                        </Text>
                    </div>

                    {/* Links */}
                    <div className='flex gap-6'>
                        <Link
                            href='/privacy'
                            className='text-gray-400 hover:text-white transition-colors text-xs uppercase tracking-wider'>
                            PRIVACY
                        </Link>
                        <Link
                            href='https://github.com/imsks/rajniti'
                            external
                            className='text-gray-400 hover:text-white transition-colors text-xs uppercase tracking-wider'>
                            GITHUB
                        </Link>
                        <Link
                            href='/about'
                            className='text-gray-400 hover:text-white transition-colors text-xs uppercase tracking-wider'>
                            ABOUT
                        </Link>
                        <Link
                            href='/contact'
                            className='text-gray-400 hover:text-white transition-colors text-xs uppercase tracking-wider'>
                            CONTACT
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    )
}
