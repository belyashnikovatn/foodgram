import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Представляю вам дипломный проект, созданный по итогам обучения в Яндекс Практикуме.
            </p>
            <p className={styles.textItem}>
              Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. 
              Понравился рецепт? Добавьте в избранное или подпишитесь на пользователя, чтобы не пропустить 
              другие его рецепты. Ваши подписки и избранные рецепты доступны в личном кабинете. Там же вы сможете 
              сменить аватарку и скачать список продуктов, необходимых для приготовления блюда. Для поиска рецептов 
              предусмотрены теги, а для рецепта предусмотрена короткая ссылка. 
            </p>
            <p className={styles.textItem}>
              Чтобы использовать все возможности сайта — нужна регистрация. Проверка адреса электронной почты не осуществляется, вы можете ввести любой email. 
            </p>
            <p className={styles.textItem}>
              Заходите и делитесь своими любимыми рецептами!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта на <a href="https://github.com/belyashnikovatn/foodgram" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              API на <a href="https://yummyinyourtummy.ru/api/" className={styles.textLink}>DRF</a>
            </p>
            <p className={styles.textItem}>
              Спецификация API на <a href="https://yummyinyourtummy.ru/api/docs/" className={styles.textLink}>ReDoc</a>
            </p>
            <p className={styles.textItem}>
              Бэкенд разработала <a href="https://github.com/belyashnikovatn" className={styles.textLink}>Таня Беляшникова</a>
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

