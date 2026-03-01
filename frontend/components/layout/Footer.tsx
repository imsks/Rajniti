import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import { Github } from "lucide-react"

export default function Footer() {
    return (
        <footer className='border-t border-gray-200/80 bg-white/80 py-3 backdrop-blur-sm'>
            <div className='mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 sm:px-6 lg:px-8'>
                <Text
                    variant='small'
                    className='text-gray-600 rounded-full border border-orange-100 bg-orange-50/70 px-3 py-1'>
                    Building with ❤️ for 🇮🇳 Democracy
                </Text>
                <div className='flex items-center gap-3'>
                    <Link
                        href='https://github.com/imsks/rajniti'
                        external
                        className='inline-flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition-colors hover:border-gray-300 hover:text-gray-700'>
                        <span className='sr-only'>GitHub</span>
                        <Github className='h-4 w-4' />
                    </Link>
                    <Text variant='small' className='text-gray-500'>
                        © {new Date().getFullYear()} Rajniti. Open source under
                        MIT License.
                    </Text>
                </div>
            </div>
        </footer>
    )
}
